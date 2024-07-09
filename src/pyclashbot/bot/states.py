import time
from pyclashbot.bot.event_dispatcher import event_dispatcher
from pyclashbot.bot.update_stats import increment_bot_failures,stat_tester

class StateTree:
    def __init__(self, job_list):
        self.job_list = job_list

    def run(self):
        print("Running statetree.run()")
        while True:
            time.sleep(1)
            stat_tester()

