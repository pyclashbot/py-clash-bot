"""Run external commands with a timeout and process-tree cleanup.

Output-capturing subprocess calls in this project go through :func:`run` here
instead of ``subprocess.run(..., shell=True)``. Commands run as an argv list with
**no shell**; on timeout the process tree is killed via ``psutil`` (one code path
on Windows/macOS/Linux), so a timed-out command normally does not leave an
orphaned child (e.g. a stuck ``adb``) running in the background.

Caveat worth knowing: the tree kill terminates the snapshot of descendants it can
enumerate. Children spawned after that snapshot, or hidden by process permissions
(an elevated ``adb`` on Windows), may survive -- in which case :func:`run` still
returns within a bounded time rather than hanging, and logs the fact.
"""

import logging
from contextlib import suppress
from os import name
from subprocess import PIPE, CompletedProcess, Popen, TimeoutExpired

import psutil

logger = logging.getLogger(__name__)

WIN32 = name == "nt"

#: Sentinel ``returncode`` meaning "the command timed out and its tree was killed".
#: Distinct from any real exit status, so callers can tell a wedged command from
#: a command that merely exited non-zero. Use :func:`timed_out` to test for it.
TIMEOUT_RETURNCODE = -1

#: Seconds allowed for a killed process to flush and close its pipes.
_DRAIN_TIMEOUT = 5.0


def timed_out(result: CompletedProcess) -> bool:
    """Return True if ``result`` came from a command that hit its timeout."""
    return result.returncode == TIMEOUT_RETURNCODE


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


def _kill_process_tree(pid: int, *, grace: float = 3.0) -> None:
    """Terminate a process and every descendant it could enumerate.

    SIGTERM the whole tree, wait briefly, then SIGKILL whatever survives. Uses
    ``psutil`` so it needs no per-platform branching (on Windows both
    ``terminate`` and ``kill`` map to ``TerminateProcess``, so the grace period
    buys nothing there).

    Never raises: an unkillable process is a degraded outcome we report to the
    caller, not an exception that would strand the caller while it holds a live
    child. The caller still has a bounded drain to fall back on.
    """
    try:
        parent = psutil.Process(pid)
    except psutil.Error:
        # NoSuchProcess: already gone. AccessDenied: another user's/elevated
        # process -- we cannot touch it. Both mean "no tree to kill from here".
        return

    try:
        procs = parent.children(recursive=True)
    except psutil.Error:
        # Could not enumerate children (permissions, or the tree exited mid-walk).
        # Kill the parent we *can* see and say so, rather than silently implying
        # the whole tree died.
        logger.warning("Could not enumerate children of pid %s; killing only the parent", pid)
        procs = []
    procs.append(parent)

    for proc in procs:
        try:
            proc.terminate()
        except psutil.Error:
            continue

    _, alive = psutil.wait_procs(procs, timeout=grace)
    for proc in alive:
        try:
            proc.kill()
        except psutil.Error:
            continue


def _abandon(proc: Popen) -> None:
    """Give up on a process that outlived both the kill ladder and the drain.

    Must never block. ``Popen`` objects reap their child in ``__del__``, which
    waits unconditionally -- so leaving one un-reaped converts a degraded
    timeout into a hang at an unpredictable later moment (or at interpreter
    exit). Instead we make a final best-effort kill and then explicitly mark the
    child as ours no longer: dropping our ``Popen`` handle without reaping leaves
    the OS to reap it, and we detach the streams so nothing keeps the pipes open.
    """
    for stream in (proc.stdout, proc.stderr, proc.stdin):
        if stream is not None:
            with suppress(OSError):
                stream.close()

    # Last resort. ``Popen.kill`` is a direct kill(2)/TerminateProcess on the pid
    # we spawned, so it still works in cases where psutil reported AccessDenied.
    with suppress(OSError, ProcessLookupError):
        proc.kill()

    # Reap only if it is already gone. Never wait: that is the hang we are
    # avoiding. ``poll()`` does a non-blocking waitpid, so this returns at once.
    with suppress(OSError, ValueError):
        proc.poll()

    # Orphan the handle so ``Popen.__del__`` cannot later block on wait().
    # Returning None from ``__del__`` is ignored, but clearing ``returncode``
    # makes CPython's internal ``_internal_poll`` a no-op on the dead child.
    with suppress(Exception):
        proc.returncode = proc.returncode if proc.returncode is not None else TIMEOUT_RETURNCODE


def run(
    args: list[str],
    *,
    timeout: float,
    capture_output: bool = True,
    text: bool = True,
    env: dict | None = None,
) -> CompletedProcess:
    """Run ``args`` (an argv list, never a shell string) with a timeout.

    On timeout the command's process tree is killed and a failed
    ``CompletedProcess`` (returncode :data:`TIMEOUT_RETURNCODE`, testable with
    :func:`timed_out`) is returned rather than raising, so callers degrade
    gracefully instead of hanging or leaking processes.

    Args:
        args: Command and arguments as a list (no shell parsing).
        timeout: Seconds to wait before killing the process tree.
        capture_output: Capture stdout/stderr via pipes (default True).
        text: Decode output as text (True) or return bytes (False).
        env: Optional environment mapping for the child process.
    """
    stdio = PIPE if capture_output else None
    empty: str | bytes = "" if text else b""
    timed_out_msg = "command timed out" if text else b"command timed out"

    # NOTE: the process is managed manually rather than via `with Popen(...)`.
    # `Popen.__exit__` calls `self.wait()` with no timeout, so returning from
    # inside a `with` block after a *failed* kill would block forever -- turning
    # "the kill didn't work" into exactly the hang this module exists to prevent.
    # Every exit path below therefore waits on a bounded budget instead.
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
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
        except TimeoutExpired:
            logger.warning("Command timed out after %ss: %s", timeout, args)
            _kill_process_tree(proc.pid)
            # Drain whatever the command wrote before the kill. If the process
            # outlived the kill (e.g. AccessDenied on an elevated adb) this times
            # out too -- we then give up on the pipes rather than block forever.
            try:
                stdout, stderr = proc.communicate(timeout=_DRAIN_TIMEOUT)
            except TimeoutExpired:
                logger.error("Command %s survived the kill; abandoning its pipes", args)
                stdout, stderr = None, None
                _abandon(proc)
            return CompletedProcess(
                args,
                returncode=TIMEOUT_RETURNCODE,
                stdout=stdout if stdout is not None else empty,
                stderr=stderr if stderr else timed_out_msg,
            )

        return CompletedProcess(args, proc.returncode, stdout, stderr)
    finally:
        # Close the pipes without waiting: on the success path the child is
        # already reaped by communicate(), and on every other path we must not
        # reintroduce an unbounded wait.
        for stream in (proc.stdout, proc.stderr):
            if stream is not None:
                with suppress(OSError):
                    stream.close()
