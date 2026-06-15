"""Run external commands with a timeout and reliable process-tree cleanup.

Output-capturing subprocess calls in this project go through :func:`run` here
instead of ``subprocess.run(..., shell=True)``. Commands run as an argv list with
**no shell**; on timeout the **whole process tree** is killed via ``psutil`` (one
code path on Windows/macOS/Linux), so a timed-out command never leaves an
orphaned child (e.g. a stuck ``adb``) running in the background.
"""

import logging
from os import name
from subprocess import PIPE, CompletedProcess, Popen, TimeoutExpired

import psutil

logger = logging.getLogger(__name__)

WIN32 = name == "nt"

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
    """Terminate a process and every descendant it spawned.

    SIGTERM the whole tree, wait briefly, then SIGKILL whatever survives. Uses
    ``psutil`` so it behaves identically on Windows/macOS/Linux (on Windows both
    signals map to ``TerminateProcess``).
    """
    try:
        parent = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return

    try:
        procs = parent.children(recursive=True)
    except psutil.Error:
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


def run(
    args: list[str],
    *,
    timeout: float,
    capture_output: bool = True,
    text: bool = True,
    env: dict | None = None,
) -> CompletedProcess:
    """Run ``args`` (an argv list, never a shell string) with a timeout.

    On timeout the command's full process tree is killed and a failed
    ``CompletedProcess`` (returncode ``-1``) is returned rather than raising, so
    callers degrade gracefully instead of hanging or leaking processes.

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

    with Popen(
        args,
        shell=False,
        stdout=stdio,
        stderr=stdio,
        text=text,
        env=env,
        **_PLATFORM_FLAGS,
    ) as proc:
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
        except TimeoutExpired:
            logger.warning("Command timed out after %ss: %s", timeout, args)
            _kill_process_tree(proc.pid)
            # Tree is dead now; drain whatever it wrote before the kill (also lets
            # the context manager exit cleanly). stdout/stderr are never None so
            # callers can `.strip()` the result without guarding the timeout path.
            try:
                stdout, stderr = proc.communicate(timeout=5)
            except TimeoutExpired:
                stdout, stderr = None, None
            return CompletedProcess(
                args,
                returncode=-1,
                stdout=stdout if stdout is not None else empty,
                stderr=stderr if stderr else timed_out_msg,
            )

    return CompletedProcess(args, proc.returncode, stdout, stderr)
