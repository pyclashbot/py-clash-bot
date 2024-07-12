from PySide6.QtCore import QObject, Signal, Slot
from pyclashbot.bot.stats import stats
import time
from pyclashbot.bot.test_state import do_fight

class StateTree(QObject):
    def __init__(self, jobs=False):
        super().__init__()
        self.jobs = jobs

    finished = Signal()

    @Slot()
    def run(self):
        print("Jobs in state tree:")
        for job_name, value in self.jobs.items():
            print('  -{:^40} : {}'.format(job_name, value))

        while True:
            do_fight()
            time.sleep(10)
