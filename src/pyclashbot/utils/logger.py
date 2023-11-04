"""import logging for file logging"""
import logging
import pprint
import threading
import time
import zipfile
from functools import wraps
from os import listdir, makedirs, remove
from os.path import basename, exists, expandvars, getmtime, join

from pyclashbot.utils.machine_info import MACHINE_INFO
from pyclashbot.utils.pastebin import upload_pastebin
from pyclashbot.utils.versioning import __version__

MODULE_NAME = "py-clash-bot"
LOGS_TO_KEEP = 10

log_dir = join(expandvars("%appdata%"), MODULE_NAME, "logs")
log_name = join(log_dir, time.strftime("%Y-%m-%d_%H-%M", time.localtime()) + ".txt")
archive_name: str = join(log_dir, "logs.zip")


def compress_logs() -> None:
    """archive will contain a large text file, all old logs appended together
    extract the file and read the text to get the old logs"""

    logs: list[str] = sorted(
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


def initalize_pylogging() -> None:
    """method to be called once to initalize python logging"""

    if not exists(log_dir):
        makedirs(log_dir)
    logging.basicConfig(
        filename=log_name,
        encoding="utf-8",
        level=logging.DEBUG,
        format="%(levelname)s:%(asctime)s %(message)s",
    )
    logging.info("Logging initialized for %s", __version__)
    logging.info(
        """
 ____  _  _       ___  __      __    ___  _   _     ____  _____  ____
(  _ \\( \\/ )___  / __)(  )    /__\\  / __)( )_( )___(  _ \\(  _  )(_  _)
 )___/ \\  /(___)( (__  )(__  /(__)\\ \\__ \\ ) _ ((___)) _ < )(_)(   )(
(__)   (__)      \\___)(____)(__)(__)(___/(_) (_)   (____/(_____) (__)
"""
    )
    logging.info(
        "Machine Info: \n%s", pprint.pformat(MACHINE_INFO, sort_dicts=False, indent=4)
    )
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
        self.card_randomizations = 0
        self.winrate: str = "00.0%"

        # job stats
        self.requests = 0
        self.request_attempts = 0
        self.deck_randomize_attempts = 0
        self.chests_unlocked = 0
        self.cards_upgraded = 0
        self.card_upgrade_attempts = 0
        self.card_mastery_reward_collections = 0
        self.free_offer_collections = 0
        self.free_offer_collection_attempts = 0
        self.chest_unlock_attempts = 0
        self.card_mastery_reward_collection_attempts = 0
        self.war_attempts = 0

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
                "winrate": self.winrate,
                "card_randomizations": self.card_randomizations,
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
        """log something to file and print to console with time and stats"""
        log_message = f"[{self.current_state}] {message}"
        logging.info(log_message)
        time_string = self.calc_time_since_start()
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
        """calculate time since start of bot using logger's
        stats and reutrn as string in hours:mins:seconds"""
        if self.start_time is not None:
            hours, remainder = divmod(time.time() - self.start_time, 3600)
            minutes, seconds = divmod(remainder, 60)
        else:
            hours, minutes, seconds = 0, 0, 0
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    @_updates_log
    def calc_win_rate(self):
        """calculate win rate using logger's stats and return as string"""
        wins = self.wins
        losses = self.losses

        if wins != 0 and losses == 0:
            return "100%"

        if wins == 0:
            return "00.0%"

        if losses == 0:
            return "100%"

        ratio = str(100 * (wins / (wins + losses)))[:4] + "%"
        return ratio

    @_updates_log
    def set_current_state(self, state_to_set):
        """set logger's current_state to state_to_set"""
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
        """increment logger's card mastery reward collection counter by 1"""
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
    def remove_card_played(self, cards_to_remove=1):
        """decremenet logger's card played counter by cards_to_remove"""
        self.cards_played -= cards_to_remove

    @_updates_log
    def add_card_upgraded(self):
        """add card upgraded to log"""
        self.cards_upgraded += 1

    @_updates_log
    def add_win(self):
        """add win to log"""
        self.wins += 1
        self.winrate = self.calc_win_rate()

    @_updates_log
    def add_loss(self):
        """add loss to log"""
        self.losses += 1
        self.winrate = self.calc_win_rate()

    @_updates_log
    def add_1v1_fight(self) -> None:
        """add fight to log"""
        self._1v1_fights += 1

    @_updates_log
    def add_card_randomization(self):
        """incremenet card_randomizations counter"""
        self.card_randomizations += 1

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

    def add_randomize_deck_attempt(self):
        """increments logger's deck_randomize_attempts by 1"""
        self.deck_randomize_attempts += 1

    def add_request_attempt(self):
        """increments logger's request_attempts by 1"""
        self.request_attempts += 1

    def add_free_offer_collection_attempt(self):
        """increments logger's free_offer_collection_attempts by 1"""
        self.free_offer_collection_attempts += 1

    def add_card_upgrade_attempt(self):
        """increments logger's card_upgrade_attempts by 1"""
        self.card_upgrade_attempts += 1

    def add_chest_unlock_attempt(self):
        """increments logger's chest_unlock_attempts by 1"""
        self.chest_unlock_attempts += 1

    def add_card_mastery_reward_collection_attempt(self):
        """increments logger's card_mastery_reward_collection_attempts by 1"""
        self.card_mastery_reward_collection_attempts += 1

    def add_war_attempt(self):
        """increments logger's war_attempts by 1"""
        self.war_attempts += 1

    def get_1v1_fights(self) -> int:
        """returns logger's 1v1_fights stat"""
        return self._1v1_fights

    def get_2v2_fights(self) -> int:
        """returns logger's 2v2_fights stat"""
        return self._2v2_fights

    def get_cards_played(self) -> int:
        """returns logger's cards_played stat"""
        return self.cards_played

    def get_free_offer_collections(self) -> int:
        """returns logger's free_offer_collections stat"""
        return self.free_offer_collections

    def get_requests(self) -> int:
        """returns logger's requests stat"""
        return self.requests

    def get_card_upgrades(self) -> int:
        """returns logger's cards_upgraded stat"""
        return self.cards_upgraded

    def get_chests_opened(self):
        """return chests_unlocked stat"""
        return self.chests_unlocked

    def check_if_can_open_chests(self, increment):
        """check if can open chests using logger's games_played and
        open_chests attempts stats and user input increment arg"""

        if increment == 1:
            self.log(f"Increment is {increment} so can always open chests")
            return True

        # count chest_unlock_attempts
        chest_unlock_attempts = self.chest_unlock_attempts

        # count games
        games_played = self._1v1_fights + self._2v2_fights + self.war_fights

        # if chest_unlock_attempts is zero return true
        if chest_unlock_attempts == 0:
            self.log(
                f"Can open chests. {games_played} Games and {chest_unlock_attempts} Attempts"
            )
            return True

        # if games_played is zero return true
        if games_played == 0:
            self.log(
                f"Can open chests. {games_played} Games and {chest_unlock_attempts} Attempts"
            )
            return True

        # if games_played / int(increment) > chest_unlock_attempts
        if games_played / int(increment) >= chest_unlock_attempts:
            self.log(
                f"Can open chests. {games_played} Games and {chest_unlock_attempts} Attempts"
            )
            return True

        self.log(
            f"Cant open chests. {games_played} Games and {chest_unlock_attempts} Attempts"
        )
        return False

    def check_if_can_collect_card_mastery(self, increment) -> bool:
        """check if can collect card mastery rewards using logger's games_played and
        card_mastery_reward_collection_attempts stats and user input increment arg"""

        if increment == 1:
            self.log(f"Increment is {increment} so can always collect card mastery")
            return True

        # count card_mastery_reward_collection_attempts
        card_mastery_attempts = self.card_mastery_reward_collection_attempts

        # count games
        games_played = self._1v1_fights + self._2v2_fights + self.war_fights

        # if card_mastery_reward_collection_attempts is zero return true
        if card_mastery_attempts == 0:
            self.log(
                f"Can do card mastery. {games_played} Games and {card_mastery_attempts} Attempts"
            )
            return True

        # if games_played is zero return true
        if games_played == 0:
            self.log(
                f"Can do card mastery. {games_played} Games and {card_mastery_attempts} Attempts"
            )
            return True

        # if games_played / int(increment) > card_mastery_reward_collection_attempts
        if games_played / int(increment) >= card_mastery_attempts:
            self.log(
                f"Can do card mastery. {games_played} Games & {card_mastery_attempts} Attempts"
            )
            return True

        self.log(
            f"Cant do card mastery. {games_played} Games and {card_mastery_attempts} Attempts"
        )
        return False

    def check_if_can_do_war(self, increment) -> bool:
        if increment == 1:
            self.log(f"Increment is {increment} so can always collect card mastery")
            return True

        # count war_attempts
        war_attempts = self.war_attempts

        # count games
        games_played = self._1v1_fights + self._2v2_fights + self.war_fights

        # if war_attempts is zero return true
        if war_attempts == 0:
            self.log(
                f"Can do war. {games_played} Games and {war_attempts} Attempts"
            )
            return True

        # if games_played is zero return true
        if games_played == 0:
            self.log(
                f"Can do war. {games_played} Games and {war_attempts} Attempts"
            )
            return True

        # if games_played / int(increment) > war_attempts
        if games_played / int(increment) >= war_attempts:
            self.log(
                f"Can do war. {games_played} Games & {war_attempts} Attempts"
            )
            return True

        self.log(
            f"Cant do war. {games_played} Games and {war_attempts} Attempts"
        )
        return False

    def check_if_can_card_upgrade(self, increment):
        """check if can upgrade cards using logger's games_played and
        card_upgrade_attempts stats and user input increment arg"""

        if increment == 1:
            self.log(f"Increment is {increment} so can always upgrade cards")
            return True

        # count card_upgrade_attempts
        card_upgrade_attempts = self.card_upgrade_attempts

        # count games
        games_played = self._1v1_fights + self._2v2_fights + self.war_fights

        # if card_upgrade_attempts is zero return true
        if card_upgrade_attempts == 0:
            self.log(
                f"Can upgrade. {games_played} Games and {card_upgrade_attempts} Attempts"
            )
            return True

        # if games_played is zero return true
        if games_played == 0:
            self.log(
                f"Can upgrade. {games_played} Games and {card_upgrade_attempts} Attempts"
            )
            return True

        # if games_played / int(increment) > card_upgrade_attempts
        if games_played / int(increment) >= card_upgrade_attempts:
            self.log(
                "Can upgrade bc games_played / int(increment) > card_upgrade_attempts"
            )
            return True

        self.log(
            f"Cant upgrade. {games_played} Games and {card_upgrade_attempts} Attempts"
        )
        return False

    def check_if_can_request(self, increment) -> bool:
        """method to check if can request given attempts, games played, and user increment input"""

        if increment == 1:
            self.log(f"Increment is {increment} so can always Request")
            return True

        # count requests
        request_attempts = self.request_attempts

        # count games
        games_played = self._1v1_fights + self._2v2_fights + self.war_fights

        # if request_attempts is zero return true
        if request_attempts == 0:
            self.log(
                f"Can request bc attempts is {request_attempts} and games played is {games_played}"
            )
            return True

        # if games_played is zero return true
        if games_played == 0:
            self.log(
                f"Can request bc attempts is {request_attempts} and games played is {games_played}"
            )
            return True

        # if games_played / int(increment) > request_attempts
        if games_played / int(increment) >= request_attempts:
            self.log(
                f"Can request. attempts = {request_attempts} & games played = {games_played}"
            )
            return True

        self.log(f"Cant request. {games_played} Games and {request_attempts} Attempts")
        return False

    def check_if_can_collect_free_offer(self, increment) -> bool:
        """method to check if can collect free offers given
        attempts, games played, and user increment input"""

        if increment == 1:
            self.log(f"Increment is {increment} so can always Collect Free Offers")
            return True

        # count free_offer_collection_attempts
        free_offer_attempts = self.free_offer_collection_attempts

        # count games
        games_played = self._1v1_fights + self._2v2_fights + self.war_fights

        # if free_offer_collection_attempts is zero return true
        if free_offer_attempts == 0:
            self.log(
                f"Can collect free offer. {games_played} Games and {free_offer_attempts} Attempts"
            )
            return True

        # if games_played is zero return true
        if games_played == 0:
            self.log(
                f"Can collect free offer. {games_played} Games and {free_offer_attempts} Attempts"
            )
            return True

        # if games_played / int(increment) > free_offer_collection_attempts
        if games_played / int(increment) >= free_offer_attempts:
            self.log(
                f"Can collect free offer. {games_played} Games and {free_offer_attempts} Attempts"
            )
            return True

        self.log(
            f"Cant do free offer. {games_played} Games and {free_offer_attempts} Attempts"
        )
        return False

    def check_if_can_randomize_deck(self, increment):
        """method to check if can randomize deck given
        attempts, games played, and user increment input"""

        if increment == 1:
            self.log(f"Increment is {increment} so can always randomize deck")
            return True

        # count free_offer_collection_attempts
        deck_randomize_attempts = self.deck_randomize_attempts

        # count games
        games_played = self._1v1_fights + self._2v2_fights + self.war_fights

        # if deck_randomize_attempts is zero return true
        if deck_randomize_attempts == 0:
            self.log(
                f"Can randomize deck. {games_played} Games and {deck_randomize_attempts} Attempts"
            )
            return True

        # if games_played is zero return true
        if games_played == 0:
            self.log(
                f"Can randomize deck. {games_played} Games and {deck_randomize_attempts} Attempts"
            )
            return True

        # if games_played / int(increment) > deck_randomize_attempts
        if games_played / int(increment) >= deck_randomize_attempts:
            self.log(
                f"Can randomize deck. {games_played} Games and {deck_randomize_attempts} Attempts"
            )
            return True

        self.log(
            f"Cant randomize deck. {games_played} Games and {deck_randomize_attempts} Attempts"
        )
        return False

    def update_time_of_last_request(self, input_time) -> None:
        """sets logger's time_of_last_request to input_time"""
        self.time_of_last_request = input_time

    def update_time_of_last_free_offer_collection(self, input_time) -> None:
        """sets logger's time_of_last_free_offer_collection to input_time"""
        self.time_of_last_free_offer_collection = input_time

    def update_time_of_last_card_upgrade(self, input_time) -> None:
        """sets logger's time_of_last_card_upgrade to input_time"""
        self.time_of_last_card_upgrade = input_time

    def log_job_dictionary(self, job_dictionary: dict[str, str | int]) -> None:
        """method for logging the job dictionary
        args:
            job_dictionary: the job dictionary to log
        returns:
            None
        """
        user_toggle_keys_and_values = []
        increment_user_input_keys_and_values = []

        for key, value in job_dictionary.items():
            if "increment_user_input" in key:
                increment_user_input_keys_and_values.append((key, value))
            else:
                user_toggle_keys_and_values.append((key, value))

        self.log("-------------------------------")
        self.log("------Job Dictionary:----------")
        self.log("-------------------------------")

        self.log("User Toggle Keys and Values:")
        for key, value in user_toggle_keys_and_values:
            while len(key) < 45:
                key += " "
            self.log(f"     -{key}:           {value}")

        self.log("-------------------------------")
        self.log("Increment User Input Keys and Values:")
        for key, value in increment_user_input_keys_and_values:
            while len(key) < 45:
                key += " "
            self.log(f"     -{key}:              [{value}]")

        self.log("-------------------------------")
        self.log("-------------------------------")
        self.log("-------------------------------\n\n")

    def upload_log(self) -> str | None:
        """method to upload log to pastebin"""
        with open(log_name, "r", encoding="utf-8") as log_file:
            return upload_pastebin(
                f"py-clash-bot log ({basename(log_name)})", log_file.read()
            )


if __name__ == "__main__":
    initalize_pylogging()
    logger = Logger()
