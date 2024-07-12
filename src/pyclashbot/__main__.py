import sys
from pyclashbot.bot.stats import window, app
from pyclashbot.bot.states import StateTree
from PySide6.QtCore import QThread

def main():
    window.start_button.clicked.connect(on_start_button_clicked)
    window.show()
    sys.exit(app.exec())



def start_worker_thread():
    thread = QThread()
    jobs = window.get_checkboxes()  # Correct instance of Layout class
    worker = StateTree(jobs=jobs)
    worker.moveToThread(thread)

    thread.started.connect(worker.run)
    worker.finished.connect(thread.quit)
    worker.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)

    # Ensure the thread and worker are properly managed
    window.thread = thread
    window.worker = worker

    thread.start()

def on_start_button_clicked():
    print('Start button!')

    # Create and start the worker thread
    start_worker_thread()


if __name__ == "__main__":
    print('\n'*50)
    main()
