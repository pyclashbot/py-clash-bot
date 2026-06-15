"""Offline coverage for the subprocess timeout + process-tree cleanup helper.

These drive the helper with the running Python interpreter, so they need no
emulator and behave identically on Windows/macOS/Linux. The crux is
``test_timeout_reaps_child_tree``: a timed-out command must not leave an orphaned
grandchild running (the regression behind the PR review comment).
"""

import os
import sys
import time

import psutil

from pyclashbot.utils import subprocess as sp


def test_success_returns_completed_process():
    result = sp.run([sys.executable, "-c", "print('hi')"], timeout=10)
    assert result.returncode == 0
    assert "hi" in result.stdout


def test_timeout_returns_failed_not_raises():
    start = time.monotonic()
    result = sp.run([sys.executable, "-c", "import time; time.sleep(30)"], timeout=1)
    elapsed = time.monotonic() - start

    assert result.returncode == -1
    assert elapsed < 10, "helper waited out the full sleep instead of killing on timeout"


def test_timeout_stdout_is_empty_string_not_none():
    """Callers do result.stdout.strip(); the timeout path must never return None."""
    result = sp.run([sys.executable, "-c", "import time; time.sleep(30)"], timeout=1)
    assert result.stdout is not None
    assert result.stdout.strip() == ""  # would raise AttributeError if None


def test_timeout_reaps_child_tree(tmp_path):
    """A timed-out command's grandchild must be killed, not orphaned."""
    pidfile = tmp_path / "grandchild.pid"
    script = (
        "import subprocess, sys, time;"
        "child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)']);"
        f"open({str(pidfile)!r}, 'w').write(str(child.pid));"
        "time.sleep(60)"
    )

    result = sp.run([sys.executable, "-c", script], timeout=3)
    assert result.returncode == -1

    grandchild_pid = int(pidfile.read_text())
    # Allow a brief moment for the SIGTERM/SIGKILL ladder to take effect.
    deadline = time.monotonic() + 5
    while psutil.pid_exists(grandchild_pid) and time.monotonic() < deadline:
        time.sleep(0.1)
    assert not psutil.pid_exists(grandchild_pid), "grandchild was orphaned after timeout"


def test_always_runs_without_a_shell(monkeypatch):
    seen: dict = {}
    real_popen = sp.Popen

    def spy(*args, **kwargs):
        seen.update(kwargs)
        return real_popen(*args, **kwargs)

    monkeypatch.setattr(sp, "Popen", spy)
    sp.run([sys.executable, "-c", "pass"], timeout=10)
    assert seen.get("shell") is False


def test_binary_output_returns_bytes():
    result = sp.run([sys.executable, "-c", "import sys; sys.stdout.write('x')"], timeout=10, text=False)
    assert isinstance(result.stdout, bytes)
    assert result.stdout == b"x"


def test_env_passed_through():
    env = {**os.environ, "PCB_TEST_VAR": "banana"}
    result = sp.run(
        [sys.executable, "-c", "import os; print(os.environ.get('PCB_TEST_VAR', ''))"],
        timeout=10,
        env=env,
    )
    assert "banana" in result.stdout
