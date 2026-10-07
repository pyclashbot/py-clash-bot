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


def test_surviving_kill_still_bounded(monkeypatch):
    real = sp.Popen

    class Unkillable(real):
        def kill(self):
            pass  # simulate a child that ignores the kill

    monkeypatch.setattr(sp, "Popen", Unkillable)
    start = time.monotonic()
    with pytest.raises(subprocess.TimeoutExpired):
        sp.run([sys.executable, "-c", "import time; time.sleep(8)"], timeout=1)
    assert time.monotonic() - start < 20
