"""Run external commands with a timeout; kills their process trees if they overrun."""

import logging
import os
import signal
import subprocess
from contextlib import suppress
from subprocess import PIPE, CompletedProcess, Popen, TimeoutExpired
from typing import Any

logger = logging.getLogger(__name__)

WIN32 = os.name == "nt"

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
    _PLATFORM_FLAGS: dict[str, Any] = {"startupinfo": _startupinfo, "creationflags": CREATE_NO_WINDOW}
else:
    # A new session makes the child its own process-group leader, so a timeout
    # can signal the child and every descendant with a single killpg.
    _PLATFORM_FLAGS: dict[str, Any] = {"start_new_session": True}


def _kill_tree(proc: Popen) -> None:
    """Kill proc and its descendants; best-effort, never raises."""
    if WIN32:
        # taskkill /T walks the tree; /F force-kills anything that ignores the
        # normal close request. Fall back to the direct child if it is absent.
        with suppress(OSError, subprocess.SubprocessError):
            subprocess.run(
                ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=10,
                check=False,
            )
        with suppress(OSError):
            proc.kill()
        return

    # start_new_session makes pgid == pid, and SIGKILL cannot be ignored by the
    # child or by grandchildren that stay in the group.
    with suppress(ProcessLookupError, PermissionError):
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    # Fallback for the unlikely case where the group lookup failed.
    with suppress(OSError):
        proc.kill()


def run(
    args: list[str],
    *,
    timeout: float,
    text: bool = True,
    env: dict | None = None,
) -> CompletedProcess:
    """Run argv (no shell) with a timeout; raises TimeoutExpired after killing."""
    proc = Popen(
        args,
        shell=False,
        stdout=PIPE,
        stderr=PIPE,
        text=text,
        env=env,
        **_PLATFORM_FLAGS,
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except TimeoutExpired:
        _kill_tree(proc)
        try:
            stdout, stderr = proc.communicate(timeout=5)  # reaps; 5s-bounded
        except TimeoutExpired:
            logger.error("Command %s survived the kill; giving up on its pipes", args)
            for stream in (proc.stdout, proc.stderr):
                if stream is not None:
                    with suppress(OSError):
                        stream.close()
            raise  # the drain's timeout still means: it didn't finish in time
        raise  # bounded drain done -- surface the timeout to the caller
    return CompletedProcess(args, proc.returncode, stdout, stderr)
