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
