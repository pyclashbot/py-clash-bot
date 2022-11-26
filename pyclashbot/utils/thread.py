import threading
import time


class StoppableThread(threading.Thread):
    def __init__(self, args, kwargs=None):
        self.args = args
        self.kwargs = kwargs
        threading.Thread.__init__(self, args=args, kwargs=kwargs)

        # The shutdown_flag is a threading. Event object that indicates whether the thread should be terminated.
        self.shutdown_flag = threading.Event()

        # ... Other thread setup code here ...

    def run(self):
        print(f"Thread #{self.ident} started")
        while not self.shutdown_flag.is_set():
            # ... Job code here ...
            time.sleep(0.5)
            print(f"Doing job... {self.args}")

        # ... Clean shutdown code here ...
        print(f"Thread #{self.ident} stopped")  # doesnt print for some reason

    def shutdown(self, join=False):
        self.shutdown_flag.set()
        if join:
            # wait for the thread to close
            self.join()  # this will block the gui


class PausableThread(StoppableThread):
    def __init__(self, args, kwargs=None):
        super().__init__(args, kwargs)
        self.pause_flag = threading.Event()

    def shutdown(self, join=False):
        self.pause_flag.clear()  # clear pause flag to allow thread to shutdown
        self.shutdown_flag.set()
        if join:
            # wait for the thread to close
            self.join()  # this will block the gui

    def toggle_pause(self):
        """Toggle the pause flag of the thread.

        Returns:
            bool: The new state of the pause flag.
        """
        if self.pause_flag.is_set():
            self.pause_flag.clear()
            return False
        else:
            self.pause_flag.set()
            return True
