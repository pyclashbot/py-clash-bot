import threading
import time
from functools import wraps
from os import makedirs
from os.path import exists, expandvars, join

MODULE_NAME = "py-clash-bot"

top_level = join(expandvars("%appdata%"), MODULE_NAME)


class Logger:
    """Class for logging. Allows for cross-thread, console and file logging.

    Args:
        stats (dict[str, str | int] | None, optional): stats to talk between threads. Default=None.
        console_log (bool, optional): Enable console logging. Defaults to False.
        file_log (bool, optional): Enable file logging. Defaults to True.
    """

    def __init__(
        self,
        stats: dict[str, str | int] | None = None,
        console_log: bool = False,
        file_log: bool = True,
        timed: bool = True,
    ) -> None:
        # setup console log
        self.console_log = console_log
        # print buffer for console
        self.console_buffer = ""

        # setup log file
        self.file_log = file_log
        # print buffer for file
        self.file_buffer = ""
        # open log file
        if file_log:
            if not exists(top_level):
                makedirs(top_level)
            log_file_path = join(top_level, "log.txt")
            with open(log_file_path, "w", encoding="utf-8") as log_file:
                self._log_file = log_file  # noqa

        # stats for threaded communication
        self.stats = stats
        self.stats_mutex = threading.Lock()

        # immutable statistics
        self.start_time = time.time() if timed else None

        ####STATISTICS

        # fight stats
        self.wins = 0
        self.losses = 0
        self._1v1_fights = 0
        self._2v2_fights = 0
        self.cards_played = 0
        self.war_fights = 0

        # job stats
        self.requests = 0
        self.chests_unlocked = 0
        self.cards_upgraded = 0
        self.card_mastery_reward_collections = 0
        self.free_offer_collections = 0

        # restart stats
        self.auto_restarts = 0
        self.restarts_after_failure = 0
        self.most_recent_restart_time = 0

        # bot stats
        self.account_switches = 0
        self.current_status = "Idle"

        # track errored logger
        self.errored = False

        # write initial values to queue
        self._update_stats()

    def __del__(self):
        if self.file_log:
            self._log_file.close()

    def _update_log(self) -> None:
        self._update_stats()

    def _update_stats(self) -> None:
        """updates the stats with a dictionary of mutable statistics"""
        with self.stats_mutex:
            self.stats = {
                "wins": self.wins,
                "losses": self.losses,
                "1v1_fights": self._1v1_fights,
                "2v2_fights": self._2v2_fights,
                "upgrades": self.cards_upgraded,
                "requests": self.requests,
                "restarts_after_failure": self.restarts_after_failure,
                "chests_unlocked": self.chests_unlocked,
                "cards_played": self.cards_played,
                "war_fights": self.war_fights,
                "account_switches": self.account_switches,
                "card_mastery_reward_collections": self.card_mastery_reward_collections,
                "free_offer_collections": self.free_offer_collections,
                "current_status": self.current_status,
            }

    def get_stats(self):
        """get stats"""
        with self.stats_mutex:
            stats = self.stats
        if stats is not None:
            stats["time_since_start"] = self.calc_time_since_start()
        return stats

    @staticmethod
    def _updates_log(func):
        """decorator to specify functions which update the queue with statistics"""

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            self._update_log()  # pylint: disable=protected-access
            return result

        return wrapper

    def log(self, message) -> None:
        time_running_string: str = self.calc_time_since_start()

        print(f"[{time_running_string}] {message}")

    def make_time_str(self, seconds) -> str:
        """convert epoch to time

        Args:
            seconds (int): epoch time in int

        Returns:
            str: human readable time
        """
        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        return f"{hour}:{minutes:02}:{seconds:02}"

    def calc_time_since_start(self) -> str:
        if self.start_time is not None:
            hours, remainder = divmod(time.time() - self.start_time, 3600)
            minutes, seconds = divmod(remainder, 60)
        else:
            hours, minutes, seconds = 0, 0, 0
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    @_updates_log
    def add_free_offer_collection(self) -> None:
        """add level up chest collection to log"""
        self.free_offer_collections += 1

    @_updates_log
    def error(self, message: str) -> None:
        """log error message

        Args:
            message (str): error message
        """
        self.errored = True
        self.current_status = f"Error: {message}"

    @_updates_log
    def add_card_mastery_reward_collection(self) -> None:
        self.card_mastery_reward_collections = self.card_mastery_reward_collections + 1

    @_updates_log
    def add_chest_unlocked(self) -> None:
        """add chest unlocked to log"""
        self.chests_unlocked += 1

    @_updates_log
    def add_war_fight(self) -> None:
        """add card played to log"""
        self.war_fights += 1

    @_updates_log
    def add_card_played(self) -> None:
        """add card played to log"""
        self.cards_played += 1

    @_updates_log
    def add_card_upgraded(self):
        """add card upgraded to log"""
        self.cards_upgraded += 1

    @_updates_log
    def add_account_switch(self):
        """add account switch to log"""
        self.account_switches += 1

    @_updates_log
    def add_win(self):
        """add win to log"""
        self.wins += 1

    @_updates_log
    def add_loss(self):
        """add loss to log"""
        self.losses += 1

    @_updates_log
    def add_1v1_fight(self):
        """add fight to log"""
        self._1v1_fights += 1

    @_updates_log
    def add_2v2_fight(self):
        """add fight to log"""
        self._2v2_fights += 1

    @_updates_log
    def add_request(self):
        """add request to log"""
        self.requests += 1

    @_updates_log
    def change_status(self, status):
        """change status of bot in log

        Args:
            status (str): status of bot
        """
        self.current_status = status
        self.log(status)

    @_updates_log
    def add_auto_restart(self):
        """add request to log"""
        self.auto_restarts += 1

    @_updates_log
    def add_restart_after_failure(self):
        """add request to log"""
        self.restarts_after_failure += 1

    @_updates_log
    def change_most_recent_restart_time(self, time_to_set):
        """add request to log"""
        self.most_recent_restart_time = time_to_set

    def get_1v1_fights(self):
        return self._1v1_fights

    def get_2v2_fights(self):
        return self._2v2_fights
