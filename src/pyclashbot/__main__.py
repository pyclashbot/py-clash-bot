from PySide6.QtWidgets import QApplication
import sys
from pyclashbot.interface.layout import FrontEnd
from pyclashbot.bot.states import StateTree
from threading import Thread


def run_backend():
    job_list = ["fight", "upgrade", "restart"]
    state_tree = StateTree(job_list)
    state_tree.run()


def main():
    app = QApplication(sys.argv)

    # Initialize frontend
    frontend = FrontEnd()
    frontend.show()

    # Start backend in a separate thread
    backend_thread = Thread(target=run_backend)
    backend_thread.start()

    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
