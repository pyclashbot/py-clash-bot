import logging
import threading
import time
from functools import wraps
from os import makedirs
from os.path import exists, expandvars, join


def initalize_pylogging():
    """method to be called once to initalize python logging"""
    module_name = "py-clash-bot"
    log_dir = join(expandvars("%appdata%"), module_name, "logs")
    if not exists(log_dir):
        makedirs(log_dir)
    log_name = join(log_dir, time.strftime("%Y-%m-%d", time.localtime()) + ".txt")
    logging.basicConfig(
        filename=log_name,
        encoding="utf-8",
        level=logging.DEBUG,
        format="%(levelname)s:%(asctime)s %(message)s",
    )
    logging.getLogger("PIL").setLevel(logging.INFO)


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
    ):
        # stats for threaded communication
        self.stats = stats
        self.stats_mutex = threading.Lock()

        # immutable statistics
        self.start_time = time.time() if timed else None

        ####STATISTICS

        # fight stats
        self.wins = 0
        self.losses = 0
        self.fights = 0
        self.cards_played = 0

        # job stats
        self.requests = 0
        self.chests_unlocked = 0
        self.cards_upgraded = 0
        self.card_mastery_reward_collections = 0
        self.battlepass_rewards_collections = 0
        self.level_up_chest_collections = 0
        self.war_battles_fought = 0
        self.free_offer_collections = 0
        self.war_chest_collections = 0
        self.daily_challenge_reward_collections = 0

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

    def _update_log(self):
        self._update_stats()
        logging.info(self.current_status)

    def _update_stats(self):
        """updates the stats with a dictionary of mutable statistics"""
        with self.stats_mutex:
            self.stats = {
                "wins": self.wins,
                "losses": self.losses,
                "fights": self.fights,
                "requests": self.requests,
                "auto_restarts": self.auto_restarts,
                "restarts_after_failure": self.restarts_after_failure,
                "chests_unlocked": self.chests_unlocked,
                "cards_played": self.cards_played,
                "cards_upgraded": self.cards_upgraded,
                "account_switches": self.account_switches,
                "card_mastery_reward_collections": self.card_mastery_reward_collections,
                "battlepass_rewards_collections": self.battlepass_rewards_collections,
                "level_up_chest_collections": self.level_up_chest_collections,
                "war_battles_fought": self.war_battles_fought,
                "free_offer_collections": self.free_offer_collections,
                "daily_challenge_reward_collections": self.daily_challenge_reward_collections,
                "war_chest_collections": self.war_chest_collections,
                "current_status": self.current_status,
                "time_since_start": self.calc_time_since_start(),
            }

    def get_stats(self):
        """get stats"""
        with self.stats_mutex:
            stats = self.stats
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

    def calc_time_since_start(self) -> str:
        if self.start_time is not None:
            hours, remainder = divmod(time.time() - self.start_time, 3600)
            minutes, seconds = divmod(remainder, 60)
        else:
            hours, minutes, seconds = 0, 0, 0
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    @_updates_log
    def add_war_chest_collection(self):
        """add level up chest collection to log"""
        self.war_chest_collections += 1

    @_updates_log
    def add_daily_challenge_reward_collection(self):
        """daily_challenge_reward_collection to log"""
        self.daily_challenge_reward_collections += 1

    @_updates_log
    def add_free_offer_collection(self):
        """add level up chest collection to log"""
        self.free_offer_collections += 1

    @_updates_log
    def add_battlepass_reward_collection(self):
        """add battlepass collection to log"""
        self.battlepass_rewards_collections += 1

    @_updates_log
    def error(self, message: str):
        """log error message

        Args:
            message (str): error message
        """
        self.errored = True
        logging.error(message)

    @_updates_log
    def add_level_up_chest_collection(self):
        """add level up chest collection to log"""
        self.level_up_chest_collections += 1

    @_updates_log
    def add_war_battle_fought(self):
        """add war battle fought to log"""
        self.war_battles_fought += 1

    @_updates_log
    def add_card_mastery_reward_collection(self):
        self.card_mastery_reward_collections = self.card_mastery_reward_collections + 1

    @_updates_log
    def add_chest_unlocked(self):
        """add chest unlocked to log"""
        self.chests_unlocked += 1

    @_updates_log
    def add_card_played(self):
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
    def add_fight(self):
        """add fight to log"""
        self.fights += 1

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
        print(status)

    @_updates_log
    def add_auto_restart(self):
        """add request to log"""
        self.auto_restarts += 1

    @_updates_log
    def add_restart_after_failure(self):
        """add request to log"""
        self.restarts_after_failure += 1

    @_updates_log
    def change_most_recent_restart_time(self, restart_time):
        """add request to log"""
        self.most_recent_restart_time = restart_time
