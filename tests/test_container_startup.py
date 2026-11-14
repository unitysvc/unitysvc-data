"""The generic test's lifecycle and probes, without requiring Docker in CI."""

import importlib.util
import json
import threading
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace

import pytest

from unitysvc_data import doc_preset

SCRIPT = Path(__file__).parents[1] / "src/unitysvc_data/examples/container/connectivity/connectivity-v1.py"
spec = importlib.util.spec_from_file_location("container_connectivity_v1", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def manifest():
    return {
        "services": [
            {
                "name": "web",
                "image": "example/web@sha256:" + "a" * 64,
                "ports": [5678],
                "env": {"EXPLICIT": "value"},
                "resources": {"limits": {"cpu": "0.25", "memory": "268435456", "ephemeral-storage": "1073741824"}},
                "health": {"type": "exec", "command": ["/health"], "start_period_seconds": 1, "period_seconds": 1},
            }
        ]
    }


@pytest.fixture
def fake(monkeypatch):
    monkeypatch.setattr(module, "quantity", Decimal)
    monkeypatch.delenv("DOCKER_HOST", raising=False)
    monkeypatch.delenv("DOCKER_CONTEXT", raising=False)
    runner = module.DockerTest(manifest(), timeout=3)
    calls = []
    state = {"created": False, "network": False, "healthy": True, "running": True, "pull_error": False}

    def docker(*args, **kwargs):
        calls.append(args)
        output = ""
        if args[:2] == ("context", "inspect"):
            output = json.dumps("unix:///local/docker.sock")
        elif args[0] == "pull" and state["pull_error"]:
            raise RuntimeError("image pull denied")
        elif args[:2] == ("network", "create"):
            state["network"] = True
        elif args[0] == "create":
            state["created"] = True
            output = "our-container"
        elif args[0] == "inspect":
            output = json.dumps([{"State": {"Running": state["running"], "ExitCode": 42}}])
        elif args[:2] == ("ps", "-aq") and state["created"]:
            output = "our-container"
        elif args[:3] == ("network", "ls", "-q") and state["network"]:
            output = "our-network"
        code = 1 if args[0] == "exec" and not state["healthy"] else 0
        return SimpleNamespace(stdout=output, stderr="", returncode=code)

    monkeypatch.setattr(runner, "docker", docker)
    return runner, calls, state


def test_preset_is_a_normal_uploaded_connectivity_test():
    preset = doc_preset("container_connectivity")
    assert preset["category"] == "connectivity_test"
    assert preset["meta"]["runtime"] == "docker"
    assert "local_only" not in preset["meta"]
    assert preset["is_public"] is False


def test_pull_start_probe_and_cleanup(fake):
    runner, calls, _ = fake
    result = runner.run()
    assert result["success"]
    assert next(i for i, c in enumerate(calls) if c[0] == "pull") < next(
        i for i, c in enumerate(calls) if c[0] == "create"
    )
    created = next(c for c in calls if c[0] == "create")
    assert "127.0.0.1::5678/tcp" in created and "--no-healthcheck" in created
    assert "--cpus" in created and "0.25" in created and "268435456" in created
    assert "EXPLICIT=value" in created
    assert ("rm", "--force", "--volumes", "our-container") in calls
    assert ("network", "rm", "our-network") in calls
    assert all(f"label={runner.label}" in c for c in calls if c[0] == "ps" or c[:2] == ("network", "ls"))


@pytest.mark.parametrize(
    "failure,expected", [("pull_error", "pull denied"), ("healthy", "health failed"), ("running", "exit 42")]
)
def test_failures_are_reported_and_created_resources_cleaned(fake, failure, expected):
    runner, calls, state = fake
    state[failure] = failure == "pull_error"
    result = runner.run()
    assert not result["success"] and expected in result["error"]
    if state["created"]:
        assert ("rm", "--force", "--volumes", "our-container") in calls


def test_interruption_still_cleans_resources(fake, monkeypatch):
    runner, calls, _ = fake
    monkeypatch.setattr(runner, "wait_healthy", lambda: (_ for _ in ()).throw(KeyboardInterrupt()))
    assert runner.run()["error"] == "test interrupted"
    assert ("rm", "--force", "--volumes", "our-container") in calls


def test_exec_probe_timeout_is_a_failed_health_attempt(fake, monkeypatch):
    runner, _, _ = fake

    def timeout(*_args, **_kwargs):
        raise TimeoutError("docker exec timed out")

    monkeypatch.setattr(runner, "docker", timeout)
    service = manifest()["services"][0]
    assert not runner.probe("id", service, service["health"], {})


def test_unsupported_hardware_fails_and_cleans_the_network(fake):
    runner, calls, _ = fake
    runner.manifest["services"][0]["resources"]["limits"]["nvidia.com/gpu"] = "1"
    result = runner.run()
    assert not result["success"] and "extended resources" in result["error"]
    assert ("network", "rm", "our-network") in calls


def test_http_and_tcp_checks():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(204 if self.path == "/healthy" else 500)
            self.end_headers()

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        runner = module.DockerTest(manifest(), timeout=3)
        service = manifest()["services"][0]
        inspected = {"NetworkSettings": {"Ports": {"5678/tcp": [{"HostPort": str(server.server_port)}]}}}
        assert runner.probe("id", service, {"type": "http", "path": "/healthy"}, inspected)
        assert not runner.probe("id", service, {"type": "http", "path": "/bad"}, inspected)
        assert runner.probe("id", service, {"type": "tcp"}, inspected)
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
