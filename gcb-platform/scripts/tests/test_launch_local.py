"""Launcher contracts without starting processes, opening ports, or touching databases."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, call, patch


SCRIPT = Path(__file__).resolve().parents[1] / "launch_local.py"
SPEC = importlib.util.spec_from_file_location("gcb_launch_local", SCRIPT)
launcher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(launcher)


class DependencyInstallationTests(unittest.TestCase):
    def test_existing_venv_without_pip_is_bootstrapped_before_install(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            backend, frontend, state = root / "backend", root / "frontend", root / "state"
            python = backend / ".venv/bin/python"
            python.parent.mkdir(parents=True)
            python.write_text("existing interpreter placeholder")
            frontend.mkdir()
            state.mkdir()
            (backend / "requirements.txt").write_text("example-package==1.0\n")
            (frontend / "package-lock.json").write_text("{}")
            with patch.object(launcher, "BACKEND", backend), \
                 patch.object(launcher, "FRONTEND", frontend), \
                 patch.object(launcher, "STATE", state), \
                 patch.object(launcher, "available", return_value=False) as available, \
                 patch.object(launcher, "run") as run:
                result = launcher.install_dependencies(python, create=False)
            available.assert_called_once_with([str(python), "-m", "pip", "--version"])
            self.assertEqual(run.call_args_list, [
                call([str(python), "-m", "ensurepip", "--upgrade"]),
                call([str(python), "-m", "pip", "install", "-r", "requirements.txt"], cwd=backend),
                call(["npm", "ci"], cwd=frontend),
            ])
            self.assertEqual(result, python)
            self.assertEqual(python.read_text(), "existing interpreter placeholder")
            self.assertTrue((state / "backend-dependencies").is_file())
            self.assertTrue((state / "frontend-dependencies").is_file())


class DockerReadinessTests(unittest.TestCase):
    def test_ready_docker_never_launches_desktop(self):
        with patch.object(launcher, "available", return_value=True), patch.object(launcher, "run") as run:
            launcher.docker_ready()
        run.assert_not_called()

    def test_macos_launches_desktop_then_waits_for_daemon(self):
        with patch.object(launcher, "available", side_effect=[False, False, True]) as available, \
             patch.object(launcher.platform, "system", return_value="Darwin"), \
             patch.object(launcher, "run") as run, \
             patch.object(launcher.time, "monotonic", side_effect=[0, 1, 3]), \
             patch.object(launcher.time, "sleep") as sleep, contextlib.redirect_stdout(io.StringIO()):
            launcher.docker_ready()
        run.assert_called_once_with(["open", "-a", "Docker"])
        self.assertEqual(available.call_args_list, [call(["docker", "info"])] * 3)
        sleep.assert_called_once_with(2)

    def test_macos_daemon_wait_is_bounded(self):
        with patch.object(launcher, "available", return_value=False), \
             patch.object(launcher.platform, "system", return_value="Darwin"), \
             patch.object(launcher, "run") as run, \
             patch.object(launcher.time, "monotonic", side_effect=[0, 1, 120]), \
             patch.object(launcher.time, "sleep") as sleep, contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, "120 seconds"):
                launcher.docker_ready()
        run.assert_called_once_with(["open", "-a", "Docker"])
        sleep.assert_called_once_with(2)

    def test_non_macos_does_not_invoke_open(self):
        with patch.object(launcher, "available", return_value=False), \
             patch.object(launcher.platform, "system", return_value="Linux"), \
             patch.object(launcher, "run") as run:
            with self.assertRaisesRegex(RuntimeError, "Start the Docker daemon"):
                launcher.docker_ready()
        run.assert_not_called()


class ProcessTests(unittest.TestCase):
    def test_occupied_port_is_reported_without_a_real_socket(self):
        with patch.object(launcher.socket, "socket") as socket:
            socket.return_value.__enter__.return_value.bind.side_effect = OSError("occupied")
            with self.assertRaisesRegex(RuntimeError, "Port 3001 is already in use"):
                launcher.port_free(3001)
        socket.return_value.__enter__.return_value.bind.assert_called_once_with(("127.0.0.1", 3001))

    def test_cleanup_targets_child_groups_in_reverse_then_escalates(self):
        backend, frontend = Mock(pid=101), Mock(pid=102)
        backend.wait.side_effect = [subprocess.TimeoutExpired("backend", 5), None]
        with patch.object(launcher.os, "killpg") as kill:
            launcher.stop_children([backend, frontend])
        self.assertEqual(kill.call_args_list, [call(102, signal.SIGTERM), call(101, signal.SIGTERM), call(101, signal.SIGKILL)])
        self.assertEqual(backend.wait.call_args_list, [call(timeout=5), call()])
        frontend.wait.assert_called_once_with(timeout=5)

    def test_cleanup_tolerates_already_exited_child(self):
        child = Mock(pid=101)
        with patch.object(launcher.os, "killpg", side_effect=ProcessLookupError):
            launcher.stop_children([child])
        child.wait.assert_called_once_with(timeout=5)

    def test_readiness_reports_dead_child_without_http_request(self):
        child = Mock()
        child.poll.return_value = 1
        with patch.object(launcher.time, "monotonic", side_effect=[0, 1]), \
             patch.object(launcher.urllib.request, "build_opener") as opener:
            with self.assertRaisesRegex(RuntimeError, "development server exited"):
                launcher.wait_for_url("http://127.0.0.1:8001/health", [child])
        opener.return_value.open.assert_not_called()


class LauncherMainTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.state = Path(self.temp.name) / "state"
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(launcher, "STATE", self.state))
        self.stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
        self.prerequisites = self.stack.enter_context(patch.object(launcher, "prerequisites"))
        self.stack.enter_context(patch.object(launcher, "backend_python", return_value=(Path("/fake/python"), False)))
        self.ports = self.stack.enter_context(patch.object(launcher, "port_free"))
        self.docker = self.stack.enter_context(patch.object(launcher, "docker_ready"))
        self.local_docker = self.stack.enter_context(patch.object(launcher, "require_local_docker", return_value="unix:///fake/docker.sock"))
        self.owner = self.stack.enter_context(patch.object(launcher, "owner", return_value=None))
        self.kill = self.stack.enter_context(patch.object(launcher.os, "killpg"))
        self.sleep = self.stack.enter_context(patch.object(launcher.time, "sleep"))
        self.run = self.stack.enter_context(patch.object(launcher, "run"))
        self.install = self.stack.enter_context(patch.object(launcher, "install_dependencies", return_value=Path("/fake/python")))
        self.stack.enter_context(patch.object(launcher, "available", return_value=True))
        self.popen = self.stack.enter_context(patch.object(launcher.subprocess, "Popen"))
        self.wait = self.stack.enter_context(patch.object(launcher, "wait_for_url"))
        self.stop = self.stack.enter_context(patch.object(launcher, "stop_children"))
        self.stack.enter_context(patch.object(launcher.signal, "signal"))
        self.stack.enter_context(patch.object(launcher.os, "umask"))
        self.flock = self.stack.enter_context(patch.object(launcher.fcntl, "flock"))
        self.stack.enter_context(patch.dict(os.environ, {
            "DOCKER_HOST": "tcp://remote.invalid:2376", "DOCKER_CONTEXT": "remote-production",
            "POSTGRES_PORT": "5544", "DATABASE_URL": "postgresql://remote.invalid/prod",
            "REDIS_URL": "redis://remote.invalid", "NEWSLETTER_SYNC_ENABLED": "true",
            "NEXT_PUBLIC_API_URL": "https://remote.invalid", "BACKEND_PUBLIC_URL": "https://remote.invalid",
            "NEXTAUTH_SECRET": "inherited-secret-must-not-be-used", "AUTH_URL": "https://remote.invalid",
            "NEXTAUTH_URL": "https://remote.invalid", "NEXT_PUBLIC_SITE_URL": "https://remote.invalid",
            "NEWSLETTER_PUBLIC_URL": "https://remote.invalid",
            **{key: "inherited-production-credential" for key in (
                "RESEND_API_KEY", "MAILERLITE_API_KEY", "STRIPE_SECRET_KEY",
                "STRIPE_PUBLISHABLE_KEY", "STRIPE_WEBHOOK_SECRET", "S3_ACCESS_KEY_ID",
                "S3_SECRET_ACCESS_KEY", "OPENROUTER_API_KEY",
            )},
        }))

    def main(self, *args):
        with patch.object(launcher.sys, "argv", ["launch", *args]):
            launcher.main()

    def serve(self):
        with patch.object(launcher.sys, "argv", ["launch", "--serve", "a" * 32]):
            launcher.serve()

    def assert_no_launch_side_effects(self):
        self.docker.assert_not_called()
        self.run.assert_not_called()
        self.install.assert_not_called()
        self.popen.assert_not_called()
        self.flock.assert_not_called()
        self.assertFalse(self.state.exists())

    def test_help_does_not_check_install_or_start_anything(self):
        with self.assertRaises(SystemExit) as caught:
            self.main("--help")
        self.assertEqual(caught.exception.code, 0)
        self.prerequisites.assert_not_called()
        self.ports.assert_not_called()
        self.assert_no_launch_side_effects()

    def test_check_is_read_only(self):
        self.main("--check")
        self.prerequisites.assert_called_once_with()
        self.assertEqual(self.ports.call_args_list, [call(8001), call(3001)])
        self.assert_no_launch_side_effects()

    def test_duplicate_port_aborts_before_any_state_or_start(self):
        self.ports.side_effect = RuntimeError("Port 8001 is already in use")
        with self.assertRaisesRegex(RuntimeError, "already in use"):
            self.main()
        self.assert_no_launch_side_effects()

    def test_duplicate_launcher_aborts_before_docker(self):
        self.flock.side_effect = BlockingIOError
        with self.assertRaisesRegex(RuntimeError, "already running"):
            self.serve()
        self.docker.assert_not_called()
        self.run.assert_not_called()
        self.popen.assert_not_called()

    def test_local_environment_is_pinned_and_child_failure_cleans_up(self):
        backend, frontend = Mock(), Mock()
        backend.poll.return_value = 1
        self.popen.side_effect = [backend, frontend]
        with self.assertRaisesRegex(RuntimeError, "development server stopped"):
            self.serve()
        migration = next(c for c in self.run.call_args_list if "alembic" in c.args[0])
        env = migration.kwargs["env"]
        expected = {
            "POSTGRES_PORT": "5544", "DOCKER_HOST": "unix:///fake/docker.sock",
            "DATABASE_URL": "postgresql://postgres:postgres@127.0.0.1:5544/gcb",
            "REDIS_URL": "", "NEWSLETTER_SYNC_ENABLED": "false",
            "NEXT_PUBLIC_API_URL": "http://localhost:8001", "BACKEND_PUBLIC_URL": "http://localhost:8001",
            "AUTH_URL": "http://localhost:3001", "NEXTAUTH_URL": "http://localhost:3001",
            "NEXT_PUBLIC_SITE_URL": "http://localhost:3001",
            "NEWSLETTER_PUBLIC_URL": "http://localhost:3001",
            **{key: "" for key in (
                "RESEND_API_KEY", "MAILERLITE_API_KEY", "STRIPE_SECRET_KEY",
                "STRIPE_PUBLISHABLE_KEY", "STRIPE_WEBHOOK_SECRET", "S3_ACCESS_KEY_ID",
                "S3_SECRET_ACCESS_KEY", "OPENROUTER_API_KEY",
            )},
        }
        for key, value in expected.items():
            self.assertEqual(env[key], value, key)
        self.assertNotIn("DOCKER_CONTEXT", env)
        self.assertFalse((self.state / "ready").exists())
        self.assertNotEqual(env["NEXTAUTH_SECRET"], "inherited-secret-must-not-be-used")
        self.assertEqual(env["NEXTAUTH_SECRET"], (self.state / "auth-secret").read_text())
        for spawned in self.popen.call_args_list:
            self.assertEqual(spawned.kwargs["env"], env)
            self.assertTrue(spawned.kwargs["start_new_session"])
        self.stop.assert_called_once_with([backend, frontend])

    def test_second_process_spawn_failure_stops_first_child(self):
        backend = Mock()
        self.popen.side_effect = [backend, OSError("spawn failed")]
        with self.assertRaisesRegex(OSError, "spawn failed"):
            self.serve()
        self.stop.assert_called_once_with([backend])

    def test_failed_migration_never_starts_servers(self):
        def command(command, **kwargs):
            if "alembic" in command:
                raise subprocess.CalledProcessError(1, command)
        self.run.side_effect = command
        with self.assertRaises(subprocess.CalledProcessError):
            self.serve()
        self.popen.assert_not_called()

    def test_duplicate_start_does_not_spawn_or_check_services(self):
        self.owner.return_value = {"pid": 123, "token": "a" * 32}
        self.main("start")
        self.prerequisites.assert_not_called()
        self.assert_no_launch_side_effects()

    def test_start_returns_after_matching_ready_token_and_leaves_supervisor_running(self):
        child = Mock(pid=123)
        self.popen.return_value = child
        def signal_ready():
            info = json.loads((self.state / "owner.json").read_text())
            (self.state / "ready").write_text(info["token"])
            return None
        child.poll.side_effect = signal_ready
        self.main()
        info = json.loads((self.state / "owner.json").read_text())
        self.assertEqual(info["pid"], 123)
        self.assertEqual(len(info["token"]), 32)
        command = self.popen.call_args.args[0]
        self.assertEqual(command[-2:], ["--serve", info["token"]])
        self.assertEqual(command[1], str(SCRIPT))
        self.assertTrue(self.popen.call_args.kwargs["start_new_session"])
        self.assertEqual(self.popen.call_args.kwargs["stdin"], subprocess.DEVNULL)
        self.kill.assert_not_called()
        self.docker.assert_not_called()
        self.install.assert_not_called()

    def test_start_reports_supervisor_failure_without_claiming_ready(self):
        child = Mock(pid=123)
        child.poll.return_value = 1
        self.popen.return_value = child
        with self.assertRaisesRegex(RuntimeError, "Startup failed"):
            self.main()
        self.kill.assert_not_called()

    def test_start_timeout_ignores_stale_ready_and_stops_its_supervisor(self):
        self.state.mkdir()
        (self.state / "ready").write_text("stale-token")
        child = Mock(pid=123)
        child.poll.return_value = None
        self.popen.return_value = child
        with patch.object(launcher.time, "monotonic", side_effect=[0, 0, 1200]):
            with self.assertRaisesRegex(RuntimeError, "20 minutes"):
                self.main()
        self.kill.assert_called_once_with(123, signal.SIGTERM)

    def test_simultaneous_start_refuses_second_launcher_before_spawn(self):
        self.flock.side_effect = BlockingIOError
        with self.assertRaisesRegex(RuntimeError, "start is in progress"):
            self.main()
        self.popen.assert_not_called()

    def test_close_and_stop_do_not_start_or_install(self):
        for command in ("close", "stop"):
            with self.subTest(command=command):
                self.main(command)
        self.prerequisites.assert_not_called()
        self.assert_no_launch_side_effects()
        self.kill.assert_not_called()

    def test_close_signals_only_tracked_supervisor(self):
        self.owner.side_effect = [{"pid": 123, "token": "a" * 32}, None]
        self.main("close")
        self.kill.assert_called_once_with(123, signal.SIGTERM)
        self.assert_no_launch_side_effects()

    def test_status_does_not_start_daemon_or_web_servers(self):
        with patch.object(launcher.shutil, "which", return_value=None):
            self.main("status")
        self.prerequisites.assert_not_called()
        self.assert_no_launch_side_effects()


class OwnerIdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.state = Path(self.temp.name)
        self.patch = patch.object(launcher, "STATE", self.state)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.info = {"pid": 123, "token": "a" * 32}
        (self.state / "owner.json").write_text(json.dumps(self.info))

    def test_owner_matches_script_and_unique_command_token(self):
        with patch.object(launcher.subprocess, "check_output", return_value=f"python3 {SCRIPT} --serve {'a' * 32}"):
            self.assertEqual(launcher.owner(), self.info)

    def test_reused_pid_is_not_signalled(self):
        with patch.object(launcher.subprocess, "check_output", return_value="python3 unrelated_server.py"), \
             patch.object(launcher.os, "killpg") as kill, contextlib.redirect_stdout(io.StringIO()):
            self.assertIsNone(launcher.owner())
            launcher.close()
        kill.assert_not_called()

    def test_different_launcher_token_is_not_owned(self):
        with patch.object(launcher.subprocess, "check_output", return_value=f"python3 {SCRIPT} --serve {'b' * 32}"):
            self.assertIsNone(launcher.owner())

    def test_missing_process_is_not_owned(self):
        with patch.object(launcher.subprocess, "check_output", side_effect=subprocess.CalledProcessError(1, "ps")):
            self.assertIsNone(launcher.owner())


class LocalDockerTests(unittest.TestCase):
    def test_remote_docker_host_is_refused(self):
        with patch.dict(os.environ, {"DOCKER_HOST": "tcp://remote.invalid:2376", "DOCKER_CONTEXT": ""}), \
             patch.object(launcher.subprocess, "check_output") as inspect:
            with self.assertRaisesRegex(RuntimeError, "remote Docker endpoints"):
                launcher.require_local_docker()
        inspect.assert_not_called()

    def test_context_takes_precedence_over_host_and_must_be_local(self):
        with patch.dict(os.environ, {"DOCKER_HOST": "unix:///local.sock", "DOCKER_CONTEXT": "remote"}), \
             patch.object(launcher.subprocess, "check_output", return_value="ssh://remote.invalid"):
            with self.assertRaisesRegex(RuntimeError, "remote Docker endpoints"):
                launcher.require_local_docker()

    def test_local_context_resolves_to_pinnable_socket(self):
        with patch.dict(os.environ, {"DOCKER_HOST": "", "DOCKER_CONTEXT": "desktop"}), \
             patch.object(launcher.subprocess, "check_output", return_value="unix:///local.sock\n"):
            self.assertEqual(launcher.require_local_docker(), "unix:///local.sock")


if __name__ == "__main__":
    unittest.main()
