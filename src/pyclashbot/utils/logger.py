import logging
import threading
import time
import zipfile
from functools import wraps
from os import listdir, makedirs, remove
from os.path import exists, expandvars, getmtime, join

from pyclashbot.utils.versioning import __version__

MODULE_NAME = "py-clash-bot"
LOGS_TO_KEEP = 10

log_dir = join(expandvars("%appdata%"), MODULE_NAME, "logs")
archive_name = join(log_dir, "logs.zip")


def compress_logs():
    # archive will contain a large text file, all old logs appended together
    # extract the file and read the text to get the old logs

    logs = sorted(
        [join(log_dir, log) for log in listdir(log_dir) if log.endswith(".txt")],
        key=getmtime,
    )
    if len(logs) >= LOGS_TO_KEEP:
        with zipfile.ZipFile(
            archive_name, "a" if exists(archive_name) else "w"
        ) as archive:
            for log in logs[:-LOGS_TO_KEEP]:
                archive.write(log, log.split("\\")[-1])
                remove(log)


def initalize_pylogging():
    """method to be called once to initalize python logging"""

    if not exists(log_dir):
        makedirs(log_dir)
    log_name = join(log_dir, time.strftime("%Y-%m-%d_%H-%M", time.localtime()) + ".txt")
    logging.basicConfig(
        filename=log_name,
        encoding="utf-8",
        level=logging.DEBUG,
        format="%(levelname)s:%(asctime)s %(message)s",
    )
    logging.info("Logging initialized for %s", __version__)
    compress_logs()


class Logger:
    """Class for logging. Allows for cross-thread, console and file logging.

    Args:
        stats (dict[str, str | int] | None, optional): stats to communicate
            between threads. Defaults to None.
        timed (bool, optional): whether to time the bot. Defaults to True.
    """

    def __init__(
        self,
        stats: dict[str, str | int] | None = None,
        timed: bool = True,
    ) -> None:
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
        self.request_attempts = 0
        self.chests_unlocked = 0
        self.cards_upgraded = 0
        self.card_upgrade_attempts = 0
        self.card_mastery_reward_collections = 0
        self.free_offer_collections = 0
        self.free_offer_collection_attempts = 0

        # restart stats
        self.auto_restarts = 0
        self.restarts_after_failure = 0
        self.most_recent_restart_time = 0

        # bot stats
        self.current_state = "No state"
        self.current_status = "Idle"
        self.time_of_last_request = 0
        self.time_of_last_card_upgrade = 0
        self.time_of_last_free_offer_collection = 0

        # track errored logger
        self.errored = False

        # write initial values to queue
        self._update_stats()

    def check_if_can_card_upgrade(self, increment_input):
        # parse increment arg into an int
        increment_parse_dict = {
            "25 games": 25,
            "5 games": 5,
            "1 game": 1,
        }
        increment: int = increment_parse_dict[increment_input]

        # count card_upgrade_attempts
        card_upgrade_attempts = self.card_upgrade_attempts

        # count games
        games_played = self._1v1_fights + self._2v2_fights + self.war_fights

        # if card_upgrade_attempts is zero return true
        if card_upgrade_attempts == 0:
            self.log("Can upgrade bc card_upgrade_attempts is 0")
            return True

        # if games_played is zero return true
        if games_played == 0:
            self.log("Can upgrade bc games_played is 0")
            return True

        # if games_played / increment > card_upgrade_attempts
        if games_played / increment > card_upgrade_attempts:
            self.log("Can upgrade bc games_played / increment > card_upgrade_attempts")
            return True

        self.log("Cant upgrade")
        return False

    def check_if_can_request(self, increment_input) -> bool:
        # parse increment arg into an int
        increment_parse_dict = {
            "25 games": 25,
            "5 games": 5,
            "1 game": 1,
        }
        increment: int = increment_parse_dict[increment_input]

        # count requests
        request_attempts = self.request_attempts

        # count games
        games_played = self._1v1_fights + self._2v2_fights + self.war_fights

        # if request_attempts is zero return true
        if request_attempts == 0:
            self.log("Can request bc request_attempts is 0")
            return True

        # if games_played is zero return true
        if games_played == 0:
            self.log("Can request bc games_played is 0")
            return True

        # if games_played / increment > request_attempts
        if games_played / increment > request_attempts:
            self.log("Can request bc games_played / increment > request_attempts")
            return True

        self.log("Cant request")
        return False

    def check_if_can_collect_free_offer(self, increment_input) -> bool:
        # parse increment arg into an int
        increment_parse_dict = {
            "25 games": 25,
            "5 games": 5,
            "1 game": 1,
        }
        increment: int = increment_parse_dict[increment_input]

        # count free_offer_collection_attempts
        free_offer_collection_attempts = self.free_offer_collection_attempts

        # count games
        games_played = self._1v1_fights + self._2v2_fights + self.war_fights

        # if free_offer_collection_attempts is zero return true
        if free_offer_collection_attempts == 0:
            self.log("Can collect free offer bc free_offer_collection_attempts is 0")
            return True

        # if games_played is zero return true
        if games_played == 0:
            self.log("Can collect free offer bc games_played is 0")
            return True

        # if games_played / increment > free_offer_collection_attempts
        if games_played / increment > free_offer_collection_attempts:
            self.log(
                "Can collect free offer bc games_played / increment > free_offer_collection_attempts"
            )
            return True

        self.log("Cant collect free offer")
        return False

    def update_time_of_last_request(self, input_time) -> None:
        self.time_of_last_request = input_time

    def update_time_of_last_free_offer_collection(self, input_time) -> None:
        self.time_of_last_free_offer_collection = input_time

    def update_time_of_last_card_upgrade(self, input_time) -> None:
        self.time_of_last_card_upgrade = input_time

    def _update_log(self) -> None:
        self._update_stats()
        logging.info(self.current_status)

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
        def wrapper(self: "Logger", *args, **kwargs):
            result = func(self, *args, **kwargs)
            self._update_log()  # pylint: disable=protected-access
            return result

        return wrapper

    def log(self, message) -> None:
        log_message = f"[{self.current_state}] {message}"
        logging.info(log_message)
        time_string: str = str(time.time() - self.start_time if self.start_time else 0)[
            :7
        ]
        print(f"[{self.current_state}] [{time_string}] {message}")

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
    def set_current_state(self, state_to_set):
        self.current_state = state_to_set

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
        logging.error(message)

    @_updates_log
    def add_card_mastery_reward_collection(self) -> None:
        self.card_mastery_reward_collections += 1

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
    def add_win(self):
        """add win to log"""
        self.wins += 1

    @_updates_log
    def add_loss(self):
        """add loss to log"""
        self.losses += 1

    @_updates_log
    def add_1v1_fight(self) -> None:
        """add fight to log"""
        self._1v1_fights += 1

    @_updates_log
    def add_2v2_fight(self) -> None:
        """add fight to log"""
        self._2v2_fights += 1

    @_updates_log
    def add_request(self) -> None:
        """add request to log"""
        self.requests += 1

    @_updates_log
    def change_status(self, status) -> None:
        """change status of bot in log

        Args:
            status (str): status of bot
        """
        self.current_status = status
        self.log(status)

    @_updates_log
    def add_auto_restart(self) -> None:
        """add request to log"""
        self.auto_restarts += 1

    @_updates_log
    def add_restart_after_failure(self) -> None:
        """add request to log"""
        self.restarts_after_failure += 1

    @_updates_log
    def change_most_recent_restart_time(self, time_to_set) -> None:
        """add request to log"""
        self.most_recent_restart_time = time_to_set

    def add_request_attempt(self):
        self.request_attempts += 1

    def add_free_offer_collection_attempt(self):
        self.free_offer_collection_attempts += 1

    def add_card_upgrade_attempt(self):
        self.card_upgrade_attempts += 1

    def get_1v1_fights(self) -> int:
        return self._1v1_fights

    def get_2v2_fights(self) -> int:
        return self._2v2_fights

    def get_cards_played(self) -> int:
        return self.cards_played

    def get_free_offer_collections(self) -> int:
        return self.free_offer_collections

    def get_requests(self) -> int:
        return self.requests

    def get_card_upgrades(self) -> int:
        return self.cards_upgraded

    def get_chests_opened(self):
        return self.chests_unlocked
