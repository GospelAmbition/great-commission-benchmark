"""Non-destructive refresh-script checks. All Docker commands use a fake executable.

Run: python3 -m unittest discover -s gcb-platform/scripts/tests -p 'test_refresh_local_db.py'
"""
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "refresh_local_db_from_railway.sh"
FAKE_DOCKER = r'''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
args = sys.argv[1:]
with open(os.environ['CALLS'], 'a') as log:
    log.write(json.dumps({'args': args, 'host': os.environ.get('DOCKER_HOST'), 'context': os.environ.get('DOCKER_CONTEXT')}) + '\n')
if args[:2] == ['context', 'inspect']:
    print(os.environ.get('CONTEXT_ENDPOINT', 'unix:///fake/local/docker.sock'))
elif args == ['info'] and os.environ.get('DOCKER_STOPPED') and not Path(os.environ['STARTED']).exists():
    sys.exit(1)
elif args[:1] == ['run']:
    envfile = Path(args[args.index('--env-file') + 1])
    assert envfile.stat().st_mode & 0o777 == 0o600
    contents = envfile.read_text()
    assert 'PGOPTIONS=-c default_transaction_read_only=on' in contents
    Path(os.environ['CAPTURE']).write_text(contents)
    if os.environ.get('FAIL_DUMP'):
        print('synthetic failure', file=sys.stderr)
        sys.exit(1)
    print('-- Dumped from database version ' + os.environ.get('SOURCE_MAJOR', '17') + '.11')
    print('SET transaction_timeout = 0;\nDROP SCHEMA IF EXISTS public;\nCREATE SCHEMA public;')
    if os.environ.get('OTHER_SCHEMA'):
        print('CREATE SCHEMA unrelated;')
    print('CREATE TABLE public.example (value text);\nCOPY public.example (value) FROM stdin;\nSET transaction_timeout = this is data\nCREATE SCHEMA this is data\n\\.')
elif 'pg_dump' in args:
    print('-- Dumped from database version 17.11\nCREATE SCHEMA public;\nCREATE TABLE public.original (id integer);')
elif 'psql' in args and '-c' in args:
    assert args[args.index('-c') + 1] == 'SHOW server_version_num'
    print(os.environ.get('LOCAL_VERSION', '170011'))
elif 'psql' in args:
    assert '--single-transaction' in args and 'ON_ERROR_STOP=1' in args and '-X' in args
    assert '-h' in args and args[args.index('-h') + 1] == '127.0.0.1'
    assert args[args.index('-d') + 1] == 'gcb'
    text = sys.stdin.read()
    assert text.startswith('DROP SCHEMA public CASCADE;\nCREATE SCHEMA public;\n')
    assert text.count('CREATE SCHEMA public;') == 1
    assert "COMMENT ON SCHEMA public IS 'standard public schema';" in text
    assert 'SET transaction_timeout = 0;' in text
    assert 'SET transaction_timeout = this is data' in text
    Path(os.environ['RESTORED']).write_text(text)
    if os.environ.get('FAIL_RESTORE'):
        sys.exit(1)
'''


class RefreshScriptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="gcb-refresh-fakes-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.platform = self.root / "platform"
        for path in [self.platform / "scripts", self.platform / "backend", self.root / "bin", self.root / "tmp"]:
            path.mkdir(parents=True)
        self.script = self.platform / "scripts" / SCRIPT.name
        shutil.copy(SCRIPT, self.script)
        (self.platform / "docker-compose.yml").write_text("services: {}\n")
        for name, content in [
            ("docker", FAKE_DOCKER),
            ("uname", "#!/bin/sh\necho Darwin\n"),
            ("open", '#!/bin/sh\ntouch "$STARTED"\n'),
        ]:
            path = self.root / "bin" / name
            path.write_text(content)
            path.chmod(0o755)
        self.env = dict(os.environ)
        for key in ["RAILWAY_DATABASE_URL", "DOCKER_HOST", "DOCKER_CONTEXT", "_GCB_SYNC_LOCK_HELD"]:
            self.env.pop(key, None)
        self.env.update(
            PATH=str(self.root / "bin") + ":" + os.environ["PATH"],
            TMPDIR=str(self.root / "tmp"), CALLS=str(self.root / "calls"),
            CAPTURE=str(self.root / "captured"), RESTORED=str(self.root / "restored"),
            STARTED=str(self.root / "started"),
        )
        self.marker = self.root / "must-not-execute"
        (self.platform / "backend" / ".env").write_text(
            'export RAILWAY_DATABASE_URL = "postgresql://user:fake%23password@railway.example:5555/gcb?sslmode=require" # comment\n'
            f'UNRELATED=$(touch {self.marker})\n'
        )

    def run_script(self, args=(), answer="overwrite local gcb\n", **environment):
        (self.root / "calls").write_text("")
        return subprocess.run(["bash", str(self.script), *args], input=answer, text=True,
                              capture_output=True, env=dict(self.env, **environment), timeout=10)

    def calls(self):
        return [json.loads(line) for line in (self.root / "calls").read_text().splitlines()]

    def assert_no_mutations(self):
        for call in self.calls():
            self.assertNotIn("up", call["args"])
            self.assertNotIn("run", call["args"])
            self.assertNotIn("psql", call["args"])
        self.assertFalse((self.root / "started").exists())

    def test_help_and_unknown_option_do_not_access_docker(self):
        self.assertEqual(self.run_script(["--help"]).returncode, 0)
        self.assertEqual(self.calls(), [])
        self.assertEqual(self.run_script(["--yes"]).returncode, 2)
        self.assertEqual(self.calls(), [])

    def test_decline_does_not_start_docker_or_modify_database(self):
        result = self.run_script(answer="n\n", DOCKER_STOPPED="1")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Cancelled", result.stdout)
        self.assert_no_mutations()

    def test_success_uses_private_files_read_only_source_and_exact_public_restore(self):
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PGPASSWORD=fake#password", (self.root / "captured").read_text())
        self.assertNotIn("fake#password", result.stdout + result.stderr + (self.root / "calls").read_text())
        self.assertFalse(self.marker.exists())
        self.assertTrue((self.root / "restored").exists())
        recovery = next((self.root / "tmp").glob("*/local-recovery.sql")).read_text()
        self.assertEqual(recovery.count("CREATE SCHEMA public;"), 1)
        self.assertTrue(recovery.startswith("DROP SCHEMA public CASCADE;"))
        self.assertIn("CREATE TABLE public.original", recovery)
        self.assertIn("COMMENT ON SCHEMA public IS 'standard public schema';", recovery)
        for directory in (self.root / "tmp").iterdir():
            self.assertEqual(directory.stat().st_mode & 0o777, 0o700)
            self.assertFalse((directory / "source.env").exists())
            for file in directory.iterdir():
                self.assertEqual(file.stat().st_mode & 0o777, 0o600)
        for call in self.calls():
            if call["args"][:1] != ["context"]:
                self.assertEqual(call["host"], "unix:///fake/local/docker.sock")
                self.assertIsNone(call["context"])

    def test_process_source_wins_and_restore_failure_retains_backup(self):
        result = self.run_script(FAIL_RESTORE="1", RAILWAY_DATABASE_URL="postgres://override:process-secret@other.example/otherdb")
        self.assertEqual(result.returncode, 1)
        self.assertIn("rolled back", result.stderr)
        self.assertIn("PGHOST=other.example", (self.root / "captured").read_text())
        self.assertNotIn("process-secret", result.stdout + result.stderr + (self.root / "calls").read_text())
        self.assertEqual(len(list((self.root / "tmp").glob("*/local-backup.sql"))), 1)

    def test_failed_dump_and_unknown_schema_do_not_restore(self):
        for environment in [{"FAIL_DUMP": "1"}, {"OTHER_SCHEMA": "1"}]:
            with self.subTest(environment=environment):
                result = self.run_script(**environment)
                self.assertEqual(result.returncode, 1)
                self.assertFalse((self.root / "restored").exists())

    def test_mismatched_source_or_local_major_does_not_restore(self):
        for environment in [{"SOURCE_MAJOR": "16"}, {"LOCAL_VERSION": "150015"}, {"LOCAL_VERSION": "invalid"}]:
            with self.subTest(environment=environment):
                result = self.run_script(**environment)
                self.assertEqual(result.returncode, 1)
                self.assertFalse((self.root / "restored").exists())

    def test_mac_starts_docker_only_after_confirmation(self):
        result = self.run_script(DOCKER_STOPPED="1")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.root / "started").exists())

    def test_remote_docker_host_or_context_is_rejected_before_mutation(self):
        for environment in [
            {"DOCKER_HOST": "tcp://remote.example:2375"},
            {"DOCKER_HOST": "ssh://remote.example"},
            {"CONTEXT_ENDPOINT": "ssh://remote.example"},
            {"DOCKER_CONTEXT": "remote", "DOCKER_HOST": "unix:///local.sock", "CONTEXT_ENDPOINT": "tcp://remote.example:2375"},
        ]:
            with self.subTest(environment=environment):
                result = self.run_script(**environment)
                self.assertEqual(result.returncode, 1)
                self.assertIn("local Unix socket", result.stderr)
                self.assert_no_mutations()

    def test_context_takes_precedence_and_selected_socket_is_pinned(self):
        result = self.run_script(DOCKER_CONTEXT="desktop", DOCKER_HOST="tcp://unused.example:2375")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.calls()[0]["args"][:3], ["context", "inspect", "desktop"])
        self.assertEqual(self.calls()[-1]["host"], "unix:///fake/local/docker.sock")

    def test_active_launch_refuses_sync_and_lock_releases_after_exit(self):
        state = self.root / ".local-run"
        state.mkdir()
        with (state / "launch.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            result = self.run_script()
            self.assertEqual(result.returncode, 1)
            self.assertIn("Stop ./launch", result.stderr)
            self.assertEqual(self.calls(), [])
        self.assertEqual(self.run_script(answer="n\n").returncode, 0)


if __name__ == "__main__":
    unittest.main()
