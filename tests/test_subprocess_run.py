"""Offline coverage for the subprocess timeout helper's contract.

These drive the helper with the running Python interpreter, so they need no
emulator and behave identically on Windows/macOS/Linux. The suite covers the
bounded timeout path (kill + short drain, never a hang), the timeout sentinel
(testable via ``timed_out``), the no-shell guarantee, and the never-None
stdout/stderr and env/text handling contracts.

Grandchild hygiene is out of contract: commands run without a shell, so the
direct child IS the command and nothing here is expected to spawn descendants;
that invariant is the callers' and the design's, and is not re-tested by hand.
"""

import os
import sys
import time

from pyclashbot.utils import subprocess as sp


def test_success_returns_completed_process():
    result = sp.run([sys.executable, "-c", "print('hi')"], timeout=10)
    assert result.returncode == 0
    assert "hi" in result.stdout


def test_timeout_returns_failed_not_raises():
    start = time.monotonic()
    result = sp.run([sys.executable, "-c", "import time; time.sleep(30)"], timeout=1)
    elapsed = time.monotonic() - start

    assert sp.timed_out(result)
    assert result.returncode == sp.TIMEOUT_RETURNCODE
    assert elapsed < 10, "helper waited out the full sleep instead of killing on timeout"


def test_timeout_stdout_is_empty_string_not_none():
    """Callers do result.stdout.strip(); the timeout path must never return None."""
    result = sp.run([sys.executable, "-c", "import time; time.sleep(30)"], timeout=1)
    assert result.stdout is not None
    assert result.stdout.strip() == ""  # would raise AttributeError if None


def test_unkillable_process_does_not_hang(monkeypatch):
    """A process that survives the kill must still return within a bounded time.

    ``Popen.__exit__`` calls ``wait()`` with no timeout, so returning from inside
    a ``with Popen(...)`` block after a failed kill blocks forever. Subclassing
    the real ``Popen`` with a no-op ``kill`` simulates the real case this guards:
    a command that ignores the signal.
    """
    real_popen = sp.Popen

    class UnkillablePopen(real_popen):
        def kill(self):
            pass

    monkeypatch.setattr(sp, "Popen", UnkillablePopen)

    start = time.monotonic()
    result = sp.run([sys.executable, "-c", "import time; time.sleep(8)"], timeout=1)
    elapsed = time.monotonic() - start

    assert sp.timed_out(result), "an unkilled process must still report the timeout sentinel"
    # Nominal cost is the timeout (1s) plus the drain budget (5s). Generous slack
    # for a loaded CI box; the bug under test blocked indefinitely, so any finite
    # bound catches it. The 8s sleep self-limits the orphan.
    assert elapsed < 20, f"run() took {elapsed:.1f}s -- it blocked instead of returning"


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


def test_capture_output_false_gives_empty_not_none():
    """With capture_output=False stdout/stderr must still be str/bytes, not None."""
    result = sp.run([sys.executable, "-c", "print('hi')"], timeout=10, capture_output=False)
    assert result.stdout == ""
    assert result.stderr == ""
