"""Run external commands with a timeout, killing them if they overrun.

Output-capturing subprocess calls in this project go through :func:`run` here
instead of ``subprocess.run(..., shell=True)``. Commands run as an argv list with
**no shell**, so the process we spawn IS the command: on timeout a direct
``Popen.kill()`` reaps it -- there is no shell wrapper for the real work to hide
beneath, and no recursive tree-walk to get wrong. Every exit path is bounded by
a deadline, so a wedged command costs its timeout plus a short drain, never a
hang.

One consequence: children spawned by the command itself -- the adb server daemon
that ``adb start-server`` brings up is the real case -- outlive the kill, and if
they hold the read end of our pipes there is no EOF to close the drain early.
Every exit path stays bounded either way, but such strays are not reaped here.
"""

import logging
from contextlib import suppress
from os import name
from subprocess import PIPE, CompletedProcess, Popen, TimeoutExpired

logger = logging.getLogger(__name__)

WIN32 = name == "nt"

#: ``returncode`` sentinel meaning "the command hit its timeout and was killed".
#: Cannot collide with a real exit status on Windows (exit codes are unsigned
#: there); on POSIX it equals death-by-SIGHUP (``-signum``) -- an accepted
#: trade-off, since nothing in this codebase is expected to die that way. Test
#: it with :func:`timed_out` rather than hardcoding the literal.
TIMEOUT_RETURNCODE = -1

#: Seconds a killed command gets to flush and close its pipes before we stop
#: waiting for it.
_DRAIN_TIMEOUT = 5.0

if WIN32:
    from subprocess import (  # Windows-only flags
        CREATE_NO_WINDOW,
        STARTF_USESHOWWINDOW,
        STARTF_USESTDHANDLES,
        STARTUPINFO,
        SW_HIDE,
    )

    _startupinfo = STARTUPINFO()
    _startupinfo.dwFlags |= STARTF_USESHOWWINDOW | STARTF_USESTDHANDLES
    _startupinfo.wShowWindow = SW_HIDE
    # Keep console windows from flashing in the packaged GUI build.
    _PLATFORM_FLAGS: dict = {"startupinfo": _startupinfo, "creationflags": CREATE_NO_WINDOW}
else:
    _PLATFORM_FLAGS = {}


def timed_out(result: CompletedProcess) -> bool:
    """Return True if ``result`` came from a command that hit its timeout."""
    return result.returncode == TIMEOUT_RETURNCODE


def run(
    args: list[str],
    *,
    timeout: float,
    capture_output: bool = True,
    text: bool = True,
    env: dict | None = None,
) -> CompletedProcess:
    """Run ``args`` (an argv list, never a shell string) with a timeout.

    On timeout the command is killed and a failed ``CompletedProcess``
    (returncode :data:`TIMEOUT_RETURNCODE`, testable with :func:`timed_out`) is
    returned rather than raising, so callers can degrade gracefully.
    ``stdout`` and ``stderr`` are never ``None``.

    The child is managed explicitly rather than via ``with Popen(...)``:
    ``Popen.__exit__`` calls ``wait()`` with no timeout, which would block
    forever if the child somehow survived the kill. ``Popen.__del__`` is safe --
    it polls non-blockingly and reaps lazily -- so we never wait outside the two
    bounded waits below.

    Args:
        args: Command and arguments as a list (no shell parsing).
        timeout: Seconds to wait before killing the command.
        capture_output: Capture stdout/stderr via pipes (default True).
        text: Decode output as text (True) or return bytes (False).
        env: Optional environment mapping for the child process.
    """
    stdio = PIPE if capture_output else None
    empty: str | bytes = "" if text else b""
    timed_out_msg = "command timed out" if text else b"command timed out"

    proc = Popen(
        args,
        shell=False,
        stdout=stdio,
        stderr=stdio,
        text=text,
        env=env,
        **_PLATFORM_FLAGS,
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except TimeoutExpired:
        logger.warning("Command timed out after %ss: %s", timeout, args)
        # argv means the direct child IS the command, so a direct kill suffices.
        # Suppress only OSError: an already-dead child dies as
        # ProcessLookupError, and Windows TerminateProcess on an exited-and-
        # reused handle dies as PermissionError -- both OSError subclasses.
        # Anything else at the kill site (e.g. a TypeError from a broken call)
        # is a programming bug and should propagate rather than silently leak
        # a live child; a survivor of the kill is handled by the drain below.
        with suppress(OSError):
            proc.kill()
        # Bounded drain: flush whatever it wrote before the kill, and reap it.
        try:
            stdout, stderr = proc.communicate(timeout=_DRAIN_TIMEOUT)
        except TimeoutExpired:
            # Not a real workload -- nothing here survives TerminateProcess/SIGKILL
            # -- but if it ever happens: stop waiting, close our end of the pipes,
            # and report the sentinel. returncode is deliberately left alone;
            # Popen's own cleanup reaps non-blockingly.
            logger.error("Command %s survived kill; giving up on its pipes", args)
            stdout, stderr = None, None
            for stream in (proc.stdout, proc.stderr):
                if stream is not None:
                    with suppress(OSError):
                        stream.close()
        return CompletedProcess(
            args,
            returncode=TIMEOUT_RETURNCODE,
            stdout=stdout if stdout is not None else empty,
            stderr=stderr if stderr else timed_out_msg,
        )

    # capture_output=False reads as (None, None); normalise so "never None" holds
    # on every path, not just the timeout path.
    return CompletedProcess(
        args,
        proc.returncode,
        stdout if stdout is not None else empty,
        stderr if stderr is not None else empty,
    )
