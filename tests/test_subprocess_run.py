"""Behavior coverage for subprocess.run: bounded, raises, reaps."""

import subprocess
import sys
import time

import psutil
import pytest

from pyclashbot.utils import subprocess as sp


def test_success():
    result = sp.run([sys.executable, "-c", "print('hi')"], timeout=10)
    assert result.returncode == 0
    assert result.stdout.strip() == "hi"


def test_binary_output():
    result = sp.run([sys.executable, "-c", "import sys; sys.stdout.write('x')"], timeout=10, text=False)
    assert result.stdout == b"x"


def test_timeout_raises_bounded():
    start = time.monotonic()
    with pytest.raises(subprocess.TimeoutExpired):
        sp.run([sys.executable, "-c", "import time; time.sleep(30)"], timeout=1)
    assert time.monotonic() - start < 20


def test_timeout_reaps_child(tmp_path):
    tag = tmp_path / "pid"
    script = f"import os, time; open({str(tag)!r}, 'w').write(str(os.getpid())); time.sleep(60)"
    with pytest.raises(subprocess.TimeoutExpired):
        sp.run([sys.executable, "-c", script], timeout=1)
    pid = int(tag.read_text())
    # post-kill reap may lag a moment; pid must not persist
    for _ in range(50):
        if not psutil.pid_exists(pid):
            break
        time.sleep(0.1)
    assert not psutil.pid_exists(pid), "timed-out command was orphaned"


def _wait_gone(pid: int, timeout: float = 5.0) -> bool:
    """Wait for pid to be reaped; a zombie is dead, just not yet collected."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            if psutil.Process(pid).status() == psutil.STATUS_ZOMBIE:
                return True
        except psutil.NoSuchProcess:
            return True
        time.sleep(0.05)
    return False


def test_timeout_kills_grandchild(tmp_path):
    tag = tmp_path / "pids"
    # The grandchild ignores SIGTERM so only a real tree kill (SIGKILL to the
    # group, or taskkill /F /T) can remove it.
    grandchild = "import signal, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(60)"
    child = (
        "import os, signal, subprocess, sys, time;"
        "signal.signal(signal.SIGTERM, signal.SIG_IGN);"
        f"g = subprocess.Popen([sys.executable, '-c', {grandchild!r}]);"
        f"open({str(tag)!r}, 'w').write(f'{{os.getpid()}} {{g.pid}}');"
        "time.sleep(60)"
    )
    with pytest.raises(subprocess.TimeoutExpired):
        sp.run([sys.executable, "-c", child], timeout=3)
    child_pid, grandchild_pid = (int(pid) for pid in tag.read_text().split())
    assert _wait_gone(child_pid), "timed-out child was left running"
    assert _wait_gone(grandchild_pid), "timed-out grandchild was orphaned"


def test_surviving_kill_still_bounded(monkeypatch):
    # Simulate a tree kill that does not work: the drain must still be bounded.
    monkeypatch.setattr(sp, "_kill_tree", lambda proc: None)
    start = time.monotonic()
    with pytest.raises(subprocess.TimeoutExpired):
        sp.run([sys.executable, "-c", "import time; time.sleep(8)"], timeout=1)
    assert time.monotonic() - start < 20
