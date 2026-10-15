#!/usr/bin/env python3
"""Run the existing Docker database and host development servers together."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import platform
import secrets
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
PLATFORM = ROOT / "gcb-platform"
BACKEND = PLATFORM / "backend"
FRONTEND = PLATFORM / "frontend"
STATE = ROOT / ".local-run"
COMPOSE = ["docker", "compose", "-p", "gcb-platform", "-f", str(PLATFORM / "docker-compose.yml")]


def run(command, **kwargs):
    return subprocess.run(command, check=True, **kwargs)


def available(command):
    try:
        return subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10).returncode == 0
    except subprocess.TimeoutExpired:
        return False


def prerequisites():
    for command in ("docker", "node", "npm"):
        if not shutil.which(command):
            raise RuntimeError("Install {} before running ./launch.".format(command))
    version = subprocess.check_output(["node", "-p", "process.versions.node"], text=True).strip()
    if tuple(map(int, version.split(".")[:2])) < (20, 9):
        raise RuntimeError("Node.js 20.9 or newer is required.")
    if not available(["docker", "compose", "version"]):
        raise RuntimeError("Docker Compose is required (included in Docker Desktop).")


def backend_python():
    for candidate in [BACKEND / ".venv/bin/python", BACKEND / "venv/bin/python"]:
        if candidate.exists() and available([str(candidate), "-c", "import sys; sys.exit(sys.version_info < (3, 11))"]):
            return candidate, False
    for command in ("python3.11", "python3.12", "python3"):
        candidate = shutil.which(command)
        if candidate and available([candidate, "-c", "import sys; sys.exit(sys.version_info < (3, 11))"]):
            return Path(candidate), True
    raise RuntimeError("Python 3.11+ is required for the backend; install it and run ./launch again.")


def port_free(port):
    with socket.socket() as listener:
        # Recently closed HTTP sockets can remain in TIME_WAIT after a clean stop.
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            listener.bind(("127.0.0.1", port))
        except OSError:
            raise RuntimeError("Port {} is already in use. Stop that server before running ./launch.".format(port))


def docker_ready():
    if available(["docker", "info"]):
        return
    if platform.system() != "Darwin":
        raise RuntimeError("Start the Docker daemon, then run ./launch again.")
    print("Starting Docker Desktop...", flush=True)
    run(["open", "-a", "Docker"])
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        if available(["docker", "info"]):
            return
        time.sleep(2)
    raise RuntimeError("Docker Desktop did not become ready within 120 seconds.")


def install_dependencies(python, create):
    if create:
        run([str(python), "-m", "venv", str(BACKEND / ".venv")])
        python = BACKEND / ".venv/bin/python"
    if not available([str(python), "-m", "pip", "--version"]):
        run([str(python), "-m", "ensurepip", "--upgrade"])
    for manifest, marker, command, cwd, missing in [
        (BACKEND / "requirements.txt", STATE / "backend-dependencies", [str(python), "-m", "pip", "install", "-r", "requirements.txt"], BACKEND, create),
        (FRONTEND / "package-lock.json", STATE / "frontend-dependencies", ["npm", "ci"], FRONTEND, not (FRONTEND / "node_modules/next").exists()),
    ]:
        digest = hashlib.sha256(manifest.read_bytes() + str(python).encode()).hexdigest()
        if missing or not marker.exists() or marker.read_text() != digest:
            run(command, cwd=cwd)
            marker.write_text(digest)
    return python


def wait_for_url(url, children, seconds=120):
    deadline = time.monotonic() + seconds
    # Local checks must not use a machine-wide HTTP proxy.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    while time.monotonic() < deadline:
        if any(child.poll() is not None for child in children):
            raise RuntimeError("A development server exited. See logs in {}.".format(STATE))
        try:
            with opener.open(url, timeout=2) as response:
                if response.status == 200:
                    return
        except (OSError, urllib.error.URLError):
            pass
        time.sleep(1)
    raise RuntimeError("Readiness timed out for {}. See logs in {}.".format(url, STATE))


def stop_children(children):
    for child in reversed(children):
        try:
            os.killpg(child.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    for child in children:
        try:
            child.wait(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            child.wait()


def serve():
    """The background supervisor owns its lock and every web-server process group."""
    prerequisites()
    python, create = backend_python()
    port_free(8001)
    port_free(3001)
    port = os.environ.get("POSTGRES_PORT", "5433")
    if not port.isdigit() or not 1 <= int(port) <= 65535:
        raise RuntimeError("POSTGRES_PORT must be a port number (default 5433).")
    os.umask(0o077)
    STATE.mkdir(mode=0o700, exist_ok=True)
    with (STATE / "launch.lock").open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError("./launch is already running in another terminal.")
        os.environ["DOCKER_HOST"] = require_local_docker()
        os.environ.pop("DOCKER_CONTEXT", None)
        os.environ["POSTGRES_PORT"] = port
        docker_ready()
        run(COMPOSE + ["up", "-d", "postgres"], cwd=PLATFORM)
        deadline = time.monotonic() + 60
        while not available(COMPOSE + ["exec", "-T", "postgres", "pg_isready", "-h", "127.0.0.1", "-U", "postgres", "-d", "gcb"]):
            if time.monotonic() >= deadline:
                raise RuntimeError("Local PostgreSQL did not become ready within 60 seconds.")
            time.sleep(1)
        python = install_dependencies(python, create)
        secret = STATE / "auth-secret"
        if not secret.exists():
            secret.write_text(secrets.token_urlsafe(48))
        env = dict(os.environ, DATABASE_URL="postgresql://postgres:postgres@127.0.0.1:{}/gcb".format(port), REDIS_URL="", NEWSLETTER_SYNC_ENABLED="false", CORS_ORIGINS_STR="http://localhost:3001,http://127.0.0.1:3001", NEXTAUTH_SECRET=secret.read_text(), NEXT_PUBLIC_API_URL="http://localhost:8001", BACKEND_PUBLIC_URL="http://localhost:8001", AUTH_URL="http://localhost:3001", NEXTAUTH_URL="http://localhost:3001", NEXT_PUBLIC_SITE_URL="http://localhost:3001")
        # A production snapshot retains its data; disable provider access in the
        # process instead. The separate local auth secret also prevents decrypting
        # copied Stripe credentials stored under the production auth secret.
        env.update({key: "" for key in ("RESEND_API_KEY", "MAILERLITE_API_KEY", "STRIPE_SECRET_KEY",
                                      "STRIPE_PUBLISHABLE_KEY", "STRIPE_WEBHOOK_SECRET",
                                      "S3_ACCESS_KEY_ID", "S3_SECRET_ACCESS_KEY", "OPENROUTER_API_KEY")})
        env["NEWSLETTER_PUBLIC_URL"] = "http://localhost:3001"
        run([str(python), "-m", "alembic", "upgrade", "head"], cwd=BACKEND, env=env)
        children = []
        def interrupted(_signum, _frame):
            raise KeyboardInterrupt
        signal.signal(signal.SIGTERM, interrupted)
        try:
            for command, cwd, log, url in [
                ([str(python), "-m", "uvicorn", "main:app", "--reload", "--host", "127.0.0.1", "--port", "8001"], BACKEND, "backend.log", "http://127.0.0.1:8001/health"),
                (["npm", "run", "dev", "--", "--hostname", "127.0.0.1"], FRONTEND, "frontend.log", "http://127.0.0.1:3001"),
            ]:
                with (STATE / log).open("a") as output:
                    children.append(subprocess.Popen(command, cwd=cwd, env=env, stdout=output, stderr=subprocess.STDOUT, start_new_session=True))
                wait_for_url(url, children)
            (STATE / "ready").write_text(sys.argv[-1])
            print("GCB web servers ready.", flush=True)
            while all(child.poll() is None for child in children):
                time.sleep(1)
            raise RuntimeError("A development server stopped. See logs in {}.".format(STATE))
        except KeyboardInterrupt:
            print("\nStopping local web servers...")
        finally:
            (STATE / "ready").unlink(missing_ok=True)
            stop_children(children)


def require_local_docker():
    # DOCKER_CONTEXT overrides DOCKER_HOST in the Docker CLI.
    endpoint = os.environ.get("DOCKER_HOST", "") if not os.environ.get("DOCKER_CONTEXT") else ""
    if not endpoint:
        endpoint = subprocess.check_output(
            ["docker", "context", "inspect", "--format", "{{.Endpoints.docker.Host}}"], text=True, timeout=10
        ).strip()
    if not endpoint.startswith("unix:///"):
        raise RuntimeError("Select a local Docker context (Unix socket); remote Docker endpoints are refused.")
    return endpoint


def owner():
    """Match PID plus unique command token; never signal a recycled PID."""
    try:
        info = json.loads((STATE / "owner.json").read_text())
        pid, token = int(info["pid"]), info["token"]
        if pid <= 1 or not isinstance(token, str) or len(token) != 32:
            return None
        command = subprocess.check_output(["ps", "-p", str(pid), "-o", "args="], text=True, stderr=subprocess.DEVNULL, timeout=5)
        if str(Path(__file__).resolve()) + " --serve " + token in command:
            return info
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError):
        pass
    return None


def close():
    info = owner()
    if not info:
        print("No tracked GCB web servers are running.")
        return
    try:
        os.killpg(info["pid"], signal.SIGTERM)
    except ProcessLookupError:
        return
    deadline = time.monotonic() + 20
    while owner():
        if time.monotonic() >= deadline:
            raise RuntimeError("The launcher is still stopping; inspect .local-run/launch.log and retry ./launch close.")
        time.sleep(0.25)
    print("GCB web servers stopped. Docker PostgreSQL stays running.")


def status():
    info = owner()
    ready = STATE / "ready"
    phase = "ready" if info and ready.exists() and ready.read_text() == info["token"] else "starting"
    print("GCB web servers: {}".format(phase if info else "stopped"))
    print("Frontend: http://localhost:3001\nAPI: http://localhost:8001/docs\nLogs: {}".format(STATE))
    if shutil.which("docker"):
        require_local_docker()
        if available(["docker", "info"]):
            run(COMPOSE + ["ps", "postgres"], cwd=PLATFORM)
        else:
            print("Docker daemon is stopped.")


def main():
    parser = argparse.ArgumentParser(description="Start local GCB in the background. No production sync. Logs in .local-run/.")
    parser.add_argument("command", nargs="?", default="start", choices=("start", "close", "stop", "status"))
    parser.add_argument("--check", action="store_true", help="Check prerequisites and free web ports without changing anything")
    parser.add_argument("--serve", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.serve:
        serve()
        return
    if args.command in ("close", "stop"):
        close()
        return
    if args.command == "status":
        status()
        return
    if owner():
        print("GCB is already running. Use ./launch close before restarting.")
        return
    prerequisites()
    backend_python()
    require_local_docker()
    port_free(8001)
    port_free(3001)
    if args.check:
        print("Prerequisites, local Docker context and web ports OK. No services or databases changed.")
        return
    os.umask(0o077)
    STATE.mkdir(mode=0o700, exist_ok=True)
    # Serialize simultaneous start commands until the child owns launch.lock.
    with (STATE / "start.lock").open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError("Another ./launch start is in progress.")
        if owner():
            print("GCB is already running.")
            return
        token = secrets.token_hex(16)
        with (STATE / "launch.log").open("a") as output:
            child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--serve", token],
                                     stdin=subprocess.DEVNULL, stdout=output, stderr=subprocess.STDOUT,
                                     start_new_session=True)
        (STATE / "owner.json").write_text(json.dumps({"pid": child.pid, "token": token}))
        print("Starting GCB; first launch installs dependencies. Progress: .local-run/launch.log", flush=True)
        deadline = time.monotonic() + 1200
        notice = time.monotonic() + 30
        try:
            while child.poll() is None:
                ready = STATE / "ready"
                if ready.exists() and ready.read_text() == token:
                    print("GCB ready: http://localhost:3001\nAPI: http://localhost:8001/docs\nStop: ./launch close\nLogs: {}".format(STATE))
                    return
                if time.monotonic() >= deadline:
                    raise RuntimeError("Startup exceeded 20 minutes. See .local-run/launch.log.")
                if time.monotonic() >= notice:
                    print("Still starting; see .local-run/launch.log for progress.", flush=True)
                    notice = time.monotonic() + 30
                time.sleep(0.25)
            raise RuntimeError("Startup failed. See .local-run/launch.log and backend.log/frontend.log.")
        except BaseException:
            if child.poll() is None:
                try:
                    os.killpg(child.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
            raise


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, subprocess.SubprocessError) as error:
        print("Launch failed: {}".format(error), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nLaunch cancelled.", file=sys.stderr)
        sys.exit(130)
