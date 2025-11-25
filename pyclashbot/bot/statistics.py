"""Bot statistics and state management"""

import logging
import random
import threading
import time
from functools import wraps

from pydantic import BaseModel, ConfigDict, Field


class FightStatistics(BaseModel):
    """Fight-related statistics"""

    model_config = ConfigDict(validate_assignment=True)

    wins: int = 0
    losses: int = 0
    classic_1v1_fights: int = 0
    classic_2v2_fights: int = 0
    trophy_road_1v1_fights: int = 0
    war_fights: int = 0
    friendly_crowns: int = 0
    enemy_crowns: int = 0
    current_win_streak: int = 0
    best_win_streak: int = 0


class CardStatistics(BaseModel):
    """Card-related statistics"""

    model_config = ConfigDict(validate_assignment=True)

    cards_played: int = 0
    cards_upgraded: int = 0
    card_randomizations: int = 0
    card_cycles: int = 0


class CollectionStatistics(BaseModel):
    """Collection/job statistics"""

    model_config = ConfigDict(validate_assignment=True)

    battlepass_collects: int = 0
    bannerbox_collects: int = 0
    card_mastery_reward_collections: int = 0
    chests_unlocked: int = 0
    daily_rewards: int = 0
    donates: int = 0
    requests: int = 0
    shop_offer_collections: int = 0
    war_chest_collects: int = 0
    level_up_chest_collects: int = 0
    trophy_road_reward_collections: int = 0
    season_shop_buys: int = 0
    magic_item_buys: int = 0


class RestartStatistics(BaseModel):
    """Restart-related statistics"""

    model_config = ConfigDict(validate_assignment=True)

    auto_restarts: int = 0
    restarts_after_failure: int = 0
    most_recent_restart_time: int = 0


class BotState(BaseModel):
    """Current bot state and status"""

    model_config = ConfigDict(validate_assignment=True, arbitrary_types_allowed=True)

    current_state: str = "start"
    current_status: str = "Idle"
    errored: bool = False
    action_needed: bool = False
    action_text: str = "Continue"
    action_callback: object | None = None  # callable


class TimingData(BaseModel):
    """Timing-related data"""

    model_config = ConfigDict(validate_assignment=True)

    start_time: float | None = None
    time_of_last_card_upgrade: int = 0
    time_of_last_free_offer_collection: int = 0


class BotStatisticsData(BaseModel):
    """Main statistics data model composing all domains"""

    model_config = ConfigDict(validate_assignment=True)

    fights: FightStatistics = Field(default_factory=FightStatistics)
    cards: CardStatistics = Field(default_factory=CardStatistics)
    collections: CollectionStatistics = Field(default_factory=CollectionStatistics)
    restarts: RestartStatistics = Field(default_factory=RestartStatistics)
    state: BotState = Field(default_factory=BotState)
    timing: TimingData = Field(default_factory=TimingData)


class BotStatistics:
    """Class for tracking bot statistics and state. Allows for cross-thread communication.

    Args:
    ----
        stats (dict[str, str | int] | None, optional): stats to communicate
            between threads. Defaults to None.
        timed (bool, optional): whether to time the bot. Defaults to True.

    """

    def __init__(
        self,
        stats: dict[str, str | int] | None = None,
        timed: bool = True,
    ) -> None:
        # Initialize Pydantic data model
        self._data = BotStatisticsData()

        # Set start time if timed
        if timed:
            self._data.timing.start_time = time.time()

        # Thread-safe communication dict for UI
        self.stats = stats
        self.stats_mutex = threading.Lock()

        # Account management (with type annotations and thread safety)
        self.current_account: int = -1
        self.account_index_history: list[int] = []
        self.account2clan: dict[int, bool] = {}
        self.account_mutex = threading.Lock()

        # Cached properties for performance (updated in calc_win_rate)
        self.winrate: str = "0%"
        self._1v1_fights: int = 0
        self._2v2_fights: int = 0

        # Write initial values to stats dict
        self._update_stats()

    def _update_stats(self) -> None:
        """Updates the stats with a dictionary of mutable statistics (flattens Pydantic models)"""
        with self.stats_mutex:
            self.stats = {
                # fight stats from self._data.fights
                "wins": self._data.fights.wins,
                "losses": self._data.fights.losses,
                "classic_1v1_fights": self._data.fights.classic_1v1_fights,
                "classic_2v2_fights": self._data.fights.classic_2v2_fights,
                "trophy_road_1v1_fights": self._data.fights.trophy_road_1v1_fights,
                "winrate": self.winrate,  # cached property
                "current_win_streak": self._data.fights.current_win_streak,
                "best_win_streak": self._data.fights.best_win_streak,
                # card stats from self._data.cards
                "card_randomizations": self._data.cards.card_randomizations,
                "card_cycles": self._data.cards.card_cycles,
                "upgrades": self._data.cards.cards_upgraded,  # Note: UI uses "upgrades" key
                "cards_played": self._data.cards.cards_played,
                # collection stats from self._data.collections
                "war_chest_collects": self._data.collections.war_chest_collects,
                "card_mastery_reward_collections": self._data.collections.card_mastery_reward_collections,
                # restart stats from self._data.restarts
                "restarts_after_failure": self._data.restarts.restarts_after_failure,
                # state stats from self._data.state
                "current_status": self._data.state.current_status,
            }

    def get_stats(self):
        """Get stats"""
        with self.stats_mutex:
            stats = self.stats
        if stats is not None:
            stats["time_since_start"] = self.calc_time_since_start()
        return stats

    @staticmethod
    def _updates_gui(func):
        """Decorator to specify functions which update the queue with statistics"""

        @wraps(func)
        def wrapper(self: "BotStatistics", *args, **kwargs):
            result = func(self, *args, **kwargs)
            self._update_stats()
            return result

        return wrapper

    def log(self, message: str) -> None:
        """Log a message using Python's logging module with current state context.

        Args:
        ----
            message (str): The message to log

        """
        logging.info("[%s] %s", self._data.state.current_state, message)

    def calc_time_since_start(self) -> str:
        """Calculate time since start of bot using logger's
        stats and return as string in hours:mins:seconds
        """
        if self._data.timing.start_time is not None:
            hours, remainder = divmod(time.time() - self._data.timing.start_time, 3600)
            minutes, seconds = divmod(remainder, 60)
        else:
            hours, minutes, seconds = 0, 0, 0
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    def add_account_to_account_history(self, i):
        with self.account_mutex:
            self.account_index_history.append(i)

    def get_next_account(self, total_count):
        def get_lowest_value_in_dict(search_dict) -> int:
            lowest_val = None
            lowest_index = None

            for index, val in search_dict.items():
                if (lowest_val is None) or (val < lowest_val):
                    lowest_val = val
                    lowest_index = index

            if lowest_index is None:
                return 0

            # get a list of all the keys that have that value
            lowest_keys = []
            for key, value in search_dict.items():
                if int(value) == int(search_dict[lowest_index]):
                    lowest_keys.append(key)
            random_lowest_key = random.choice(lowest_keys)

            return int(random_lowest_key)

        def print_account_history_dict(index2count):
            print("\nAccount history dict:")
            print("{:^6} : {}".format("Acct #", "count"))
            for index, count in index2count.items():
                print(f"{index:^6} : {count}")
            print("\n")

        with self.account_mutex:
            # make a dict that represents index2count for each index in range(total_count)
            index2count: dict[int, int] = dict.fromkeys(range(total_count), 0)

            # populate the dict with the counts of each index in account_index_history
            for i in self.account_index_history:
                index2count[i] += 1

            # print the dict
            print_account_history_dict(index2count)

            # get the index with the lowest count
            next_account = get_lowest_value_in_dict(index2count)

            return next_account

    def increment_season_shop_buys(self):
        self._data.collections.season_shop_buys += 1

    def increment_magic_item_buys(self):
        self._data.collections.magic_item_buys += 1

    @_updates_gui
    def increment_classic_1v1_fights(self):
        self._data.fights.classic_1v1_fights += 1

    @_updates_gui
    def increment_classic_2v2_fights(self):
        self._data.fights.classic_2v2_fights += 1

    @_updates_gui
    def increment_trophy_road_fights(self):
        self._data.fights.trophy_road_1v1_fights += 1

    def increment_trophy_road_reward_collects(self):
        self._data.collections.trophy_road_reward_collections += 1

    def pick_lowest_fight_type_count(self, mode2toggle):
        return "path_of_legends"

    def is_in_clan(self):
        with self.account_mutex:
            if self.current_account in self.account2clan:
                return self.account2clan[self.current_account]
            return False

    def update_in_a_clan_value(self, in_a_clan: bool):
        with self.account_mutex:
            self.account2clan[self.current_account] = in_a_clan

    # frontend stats

    @_updates_gui
    def calc_win_rate(self):
        """Calculate win rate using logger's stats and return as string"""
        wins = self._data.fights.wins
        losses = self._data.fights.losses

        if wins == 0 and losses == 0:
            return "0%"

        if wins != 0 and losses == 0:
            return "100%"

        if wins == 0:
            return "0%"

        win_percentage = round(100 * (wins / (wins + losses)))
        return f"{win_percentage}%"

    @_updates_gui
    def set_current_state(self, state_to_set):
        """Set logger's current_state to state_to_set"""
        self._data.state.current_state = state_to_set

    @_updates_gui
    def increment_battlepass_collects(self):
        """Increment the logger's battlepass_collects count by 1."""
        self._data.collections.battlepass_collects += 1

    @_updates_gui
    def add_shop_offer_collection(self) -> None:
        """Add level up chest collection to log"""
        self._data.collections.shop_offer_collections += 1

    @_updates_gui
    def error(self, message: str) -> None:
        """Log error message and set errored flag

        Args:
        ----
            message (str): error message

        """
        self._data.state.errored = True
        logging.error(message)

    @_updates_gui
    def add_card_mastery_reward_collection(self) -> None:
        """Increment logger's card mastery reward collection counter by 1"""
        self._data.collections.card_mastery_reward_collections += 1

    @_updates_gui
    def add_chest_unlocked(self) -> None:
        """Add chest unlocked to log"""
        self._data.collections.chests_unlocked += 1

    @_updates_gui
    def add_war_fight(self) -> None:
        """Add card played to log"""
        self._data.fights.war_fights += 1

    @_updates_gui
    def add_card_played(self) -> None:
        """Add card played to log"""
        self._data.cards.cards_played += 1

    @_updates_gui
    def add_level_up_chest_collect(self):
        self._data.collections.level_up_chest_collects += 1

    @_updates_gui
    def add_card_upgraded(self):
        """Add card upgraded to log"""
        self._data.cards.cards_upgraded += 1

    @_updates_gui
    def add_win(self):
        """Add win to log"""
        self._data.fights.wins += 1
        self.winrate = self.calc_win_rate()

        # Update win streak
        self._data.fights.current_win_streak += 1
        self._data.fights.best_win_streak = max(self._data.fights.best_win_streak, self._data.fights.current_win_streak)

    @_updates_gui
    def add_loss(self):
        """Add loss to log"""
        self._data.fights.losses += 1
        self.winrate = self.calc_win_rate()

        # Reset win streak on loss
        self._data.fights.current_win_streak = 0

    @_updates_gui
    def add_1v1_fight(self) -> None:
        """Add fight to log"""
        self._1v1_fights += 1

    @_updates_gui
    def add_card_randomization(self):
        """Incremenet card_randomizations counter"""
        self._data.cards.card_randomizations += 1

    @_updates_gui
    def add_deck_cycled(self):
        """Increment card_cycles counter"""
        self._data.cards.card_cycles += 1

    @_updates_gui
    def increment_2v2_fights(self) -> None:
        """Add fight to log"""
        self._2v2_fights += 1

    @_updates_gui
    def add_request(self) -> None:
        """Add request to log"""
        self._data.collections.requests += 1

    @_updates_gui
    def add_war_chest_collect(self) -> None:
        """Add request to log"""
        self._data.collections.war_chest_collects += 1

    @_updates_gui
    def add_donate(self) -> None:
        """Add donate to log"""
        self._data.collections.donates += 1

    @_updates_gui
    def add_daily_reward(self) -> None:
        """Add donate to log"""
        self._data.collections.daily_rewards += 1

    @_updates_gui
    def change_status(self, status, action_needed=False, action_callback=None) -> None:
        """Change status of bot in log

        Args:
        ----
            status (str): status of bot
            action_needed (bool): whether an action button should be shown
            action_callback (callable): callback function to call when action is taken

        """
        self._data.state.current_status = status
        self._data.state.action_needed = action_needed
        self._data.state.action_callback = action_callback
        logging.info("[%s] %s", self._data.state.current_state, status)

    @_updates_gui
    def show_temporary_action(self, message, action_text="Retry", callback=None) -> None:
        """Show a temporary action button with the given message

        Args:
        ----
            message (str): message to display to user
            action_text (str): text for the action button
            callback (callable): function to call when action is taken
        """
        self._data.state.current_status = message
        self._data.state.action_needed = True
        self._data.state.action_text = action_text
        self._data.state.action_callback = callback
        logging.info("[%s] %s", self._data.state.current_state, message)

    @_updates_gui
    def add_restart_after_failure(self) -> None:
        """Add request to log"""
        self._data.restarts.restarts_after_failure += 1

    def add_bannerbox_collect(self):
        """Increments logger's bannerbox_collects by 1"""
        self._data.collections.bannerbox_collects += 1

    def get_1v1_fights(self) -> int:
        """Returns logger's 1v1_fights stat"""
        return self._1v1_fights

    def get_2v2_fights(self) -> int:
        """Returns logger's 2v2_fights stat"""
        return self._2v2_fights

    def get_cards_played(self) -> int:
        """Returns logger's cards_played stat"""
        return self._data.cards.cards_played

    def get_requests(self) -> int:
        """Returns logger's requests stat"""
        return self._data.collections.requests

    def get_card_upgrades(self) -> int:
        """Returns logger's cards_upgraded stat"""
        return self._data.cards.cards_upgraded

    def get_chests_opened(self):
        """Return chests_unlocked stat"""
        return self._data.collections.chests_unlocked

    def update_time_of_last_card_upgrade(self, input_time) -> None:
        """Sets logger's time_of_last_card_upgrade to input_time"""
        self._data.timing.time_of_last_card_upgrade = input_time

    def log_job_dictionary(self, job_dictionary: dict[str, str | int]) -> None:
        """Method for logging the job dictionary
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

        logging.info("-------------------------------")
        logging.info("------Job Dictionary:----------")
        logging.info("-------------------------------")

        logging.info("User Toggle Keys and Values:")
        for key, value in user_toggle_keys_and_values:
            while len(key) < 45:
                key += " "  # noqa: PLW2901
            logging.info("     -%s:           %s", key, value)

        logging.info("-------------------------------")
        logging.info("Increment User Input Keys and Values:")
        for key, value in increment_user_input_keys_and_values:
            while len(key) < 45:
                key += " "  # noqa: PLW2901
            logging.info("     -%s:              [%s]", key, value)

        logging.info("-------------------------------")
        logging.info("-------------------------------")
        logging.info("-------------------------------\n\n")

    def to_json(self) -> str:
        """Serialize statistics to JSON string

        Returns:
        -------
            str: JSON representation of bot statistics

        """
        return self._data.model_dump_json(indent=2)

    def from_json(self, json_str: str) -> None:
        """Deserialize statistics from JSON string

        Args:
        ----
            json_str (str): JSON string to deserialize

        """
        self._data = BotStatisticsData.model_validate_json(json_str)

    def save_to_file(self, filepath: str) -> None:
        """Save statistics to JSON file

        Args:
        ----
            filepath (str): Path to file where statistics will be saved

        """
        from pathlib import Path

        Path(filepath).write_text(self.to_json())
        logging.info("Statistics saved to %s", filepath)

    def load_from_file(self, filepath: str) -> None:
        """Load statistics from JSON file

        Args:
        ----
            filepath (str): Path to file from which to load statistics

        """
        from pathlib import Path

        self.from_json(Path(filepath).read_text())
        logging.info("Statistics loaded from %s", filepath)


if __name__ == "__main__":
    pass
