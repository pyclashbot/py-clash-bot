"""Run external commands with a timeout; kills them if they overrun."""

import logging
from contextlib import suppress
from os import name
from subprocess import PIPE, CompletedProcess, Popen, TimeoutExpired

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
    _PLATFORM_FLAGS: dict = {"startupinfo": _startupinfo, "creationflags": CREATE_NO_WINDOW}
else:
    _PLATFORM_FLAGS = {}


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
        with suppress(OSError):
            proc.kill()
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
