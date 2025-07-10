from os import name
from subprocess import PIPE, Popen, TimeoutExpired

# check if running on windows
WIN32 = name == "nt"
ST_INFO = None
if WIN32:
    import ctypes
    from subprocess import (
        CREATE_NO_WINDOW,
        REALTIME_PRIORITY_CLASS,
        STARTF_USESHOWWINDOW,
        STARTF_USESTDHANDLES,
        STARTUPINFO,
        SW_HIDE,
    )

    ST_INFO = STARTUPINFO()  # pyright: ignore [reportConstantRedefinition]
    ST_INFO.dwFlags |= STARTF_USESHOWWINDOW | STARTF_USESTDHANDLES | REALTIME_PRIORITY_CLASS
    ST_INFO.wShowWindow = SW_HIDE
    CR_FLAGS = CREATE_NO_WINDOW
    subprocess_flags = {
        "startupinfo": ST_INFO,
        "creationflags": CR_FLAGS,
        "start_new_session": True,
    }
else:
    subprocess_flags = {}


def _terminate_process(  # pyright: ignore [reportUnusedFunction]
    process: Popen[str],
) -> None:
    """Terminate a process forcefully on Windows."""
    handle = ctypes.windll.kernel32.OpenProcess(1, False, process.pid)
    ctypes.windll.kernel32.TerminateProcess(handle, -1)
    ctypes.windll.kernel32.CloseHandle(handle)


def run(
    args: list[str],
) -> tuple[int, str]:
    with Popen(
        args,
        shell=False,
        bufsize=-1,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True,
        universal_newlines=True,
        **subprocess_flags,
    ) as process:
        try:
            result, _ = process.communicate(timeout=5)
        except TimeoutExpired:
            if WIN32:
                # pylint: disable=protected-access
                _terminate_process(process)
            process.kill()
            result, _ = process.communicate()
            raise

        return (process.returncode, result)
