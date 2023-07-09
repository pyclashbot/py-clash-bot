import ctypes
import threading
import time
from typing import Any


class ThreadKilled(Exception):
    def __init__(self) -> None:
        super().__init__("Thread killed")


class StoppableThread(threading.Thread):
    def __init__(self, args, kwargs=None) -> None:
        self.args: Any = args
        self.kwargs = kwargs
        threading.Thread.__init__(self, args=args, kwargs=kwargs)

        # shutdown_flag is a threading Event object that says whether the thread should stop.
        self.shutdown_flag = threading.Event()

        # ... Other thread setup code here ...

    def run(self) -> None:
        print(f"Thread #{self.ident} started")
        while not self.shutdown_flag.is_set():
            # ... Job code here ...
            time.sleep(0.5)
            print(f"Doing job... {self.args}")

        # ... Clean shutdown code here ...
        print(f"Thread #{self.ident} stopped")  # doesnt print for some reason

    def shutdown(self, kill=True) -> None:
        self.shutdown_flag.set()
        if kill:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(
                self.native_id, ctypes.py_object(ThreadKilled)
            )


class PausableThread(StoppableThread):
    def __init__(self, args, kwargs=None) -> None:
        super().__init__(args, kwargs)
        self.pause_flag = threading.Event()

    def shutdown(self, kill=False) -> None:
        self.pause_flag.clear()  # clear pause flag to allow thread to shutdown
        super().shutdown(kill)  #  call parent shutdown

    def toggle_pause(self) -> bool:
        """Toggle the pause flag of the thread.

        Returns:
            bool: The new state of the pause flag.
        """
        if self.pause_flag.is_set():
            self.pause_flag.clear()
            return False
        self.pause_flag.set()
        return True
