import time
from queue import Queue
from typing import Any, Union


class Logger:
    """Class for logging. Allows for cross-thread, console and file logging.

    Args:
        queue (Union[Queue, None], optional): Queue for threaded communication. Defaults to None.
        console_log (bool, optional): Enable console logging. Defaults to False.
        file_log (bool, optional): Enable file logging. Defaults to True.
    """

    def __init__(
        self,
        queue: Union[Queue, None] = None,
        console_log: bool = False,
        file_log: bool = True,
    ):

        # track enabled log types
        self.console_log = console_log
        self.file_log = file_log

        # open log file
        if file_log:
            self._log_file = open("log.txt", "w")

        # queue for threaded communication
        self._queue = Queue() if queue is None else queue

        # immutable statistics
        self.start_time = time.time()

        # mutable statistics
        self.wins = 0
        self.losses = 0
        self.fights = 0
        self.requests = 0
        self.restarts = 0
        self.chests_unlocked = 0
        self.cards_played = 0
        self.cards_upgraded = 0
        self.account_switches = 0
        self.card_mastery_reward_collections = 0
        self.battlepass_rewards_collections = 0
        self.level_up_chest_collections = 0
        self.war_battles_fought = 0
        self.current_status = "Idle"

        # print buffer for console
        self.console_buffer = ""

        # write initial values to queue
        self._update_queue()

    def __del__(self):
        if self.file_log:
            self._log_file.close()

    def _update_queue(self):
        """updates the queue with a dictionary of mutable statistics"""
        if self._queue is None:
            return

        statistics: dict[str, Any] = {
            "wins": self.wins,
            "losses": self.losses,
            "fights": self.fights,
            "requests": self.requests,
            "restarts": self.restarts,
            "chests_unlocked": self.chests_unlocked,
            "cards_played": self.cards_played,
            "cards_upgraded": self.cards_upgraded,
            "account_switches": self.account_switches,
            "card_mastery_reward_collections": self.card_mastery_reward_collections,
            "battlepass_rewards_collections": self.battlepass_rewards_collections,
            "level_up_chest_collections": self.level_up_chest_collections,
            "war_battles_fought": self.war_battles_fought,
            "current_status": self.current_status,
        }
        self._queue.put(statistics)

    def make_timestamp(self):
        """creates a time stamp for log output

        Returns:
            str: log time stamp
        """
        output_time = time.time() - self.start_time
        output_time = int(output_time)

        return str(self.make_time_str(output_time))

    def make_win_loss_str(self):
        """creates scoreboard for log output

        Returns:
            str: log scoreboard
        """
        losses_str = f"{str(self.losses)}L"
        wins_str = f"{str(self.wins)}W"
        return f"{wins_str}|{losses_str}"

    def make_time_str(self, seconds):
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
        return "%d:%02d:%02d" % (hour, minutes, seconds)

    def log_to_console(self):
        """log to console"""

        line_with_leftside = "|----------------------------------------------------------------------------------"
        line = "-----------------------------------------------------------------------------------"

        self.add_row(line)
        self.add_row(f"|           Program uptime:           | {self.make_timestamp()}")
        self.add_row(line_with_leftside)
        self.add_row(f"|          Program restarts:          | {self.restarts}")
        self.add_row(line_with_leftside)
        self.add_row(f"|              Requests:              | {self.requests}")
        self.add_row(line_with_leftside)
        self.add_row(f"|               Fights:               | {self.fights}")
        self.add_row(line_with_leftside)
        self.add_row(
            f"|              Win rate:              | {self.make_win_loss_str()}"
        )
        self.add_row(line_with_leftside)
        self.add_row(f"|           Chests unlocked:          | {self.chests_unlocked}")
        self.add_row(line_with_leftside)
        self.add_row(f"|            Cards played:            | {self.cards_played}")
        self.add_row(line_with_leftside)
        self.add_row(f"|            Cards upgraded:          | {self.cards_upgraded}")
        self.add_row(line_with_leftside)
        self.add_row(f"|           Account switches:         | {self.account_switches}")
        self.add_row(line_with_leftside)
        self.add_row(
            f"|   Card Mastery Reward Collections   | {self.card_mastery_reward_collections}"
        )
        self.add_row(line_with_leftside)
        self.add_row(
            f"|    Battlepass Reward Collections    | {self.battlepass_rewards_collections}"
        )
        self.add_row(line_with_leftside)
        self.add_row(
            f"|     Level Up Reward Collections     | {self.level_up_chest_collections}"
        )
        self.add_row(line_with_leftside)
        self.add_row(
            f"|          War Battles Fought         | {self.war_battles_fought}"
        )
        self.add_row(line_with_leftside)

        self.add_row(f"|      Current status:      | {self.current_status}")
        self.add_row(line)
        self.print_buffer()

    def log_to_file(self):
        """log to file"""

        # log to file
        self._log_file.write(self.console_buffer)

        # clear buffer
        self.console_buffer = ""

    def line_wrap(self, line: str, width: int) -> str:
        """wrap line to width

        Args:
            line (str): line to wrap
            width (int): width to wrap line to

        Returns:
            str: wrapped line
        """

        new_line = "\n|                           | "

        # split line into words
        words = line.split(" ")

        # wrap line
        wrapped_line = ""
        current_line = ""
        for word in words:
            if len(current_line) + len(word) < width:
                current_line += f"{word} "
            else:
                wrapped_line += current_line + new_line
                current_line = f"{word} "

        # add last line
        wrapped_line += current_line

        return wrapped_line

    def add_row(self, row: str) -> None:
        """add row to log

        Args:
            row (str): row to add to log
        """
        if row is not None:
            row = self.line_wrap(row, 85)
            self.console_buffer += row + "\n"

    def print_buffer(self):
        """print log buffer"""
        print(self.console_buffer)
        self.console_buffer = ""  # clear buffer

    def add_battlepass_rewards_collection(self):
        """add battlepass rewards collection to log"""
        self.battlepass_rewards_collections += 1
        if self.console_log:
            self.log_to_console()
        self._update_queue()

    def add_level_up_chest_collection(self):
        """add level up chest collection to log"""
        self.level_up_chest_collections += 1
        if self.console_log:
            self.log_to_console()
        self._update_queue()

    def add_war_battle_fought(self):
        """add war battle fought to log"""
        self.war_battles_fought += 1
        if self.console_log:
            self.log_to_console()
        self._update_queue()

    def add_card_mastery_reward_collection(self):
        self.card_mastery_reward_collections = self.card_mastery_reward_collections + 1
        if self.console_log:
            self.log_to_console()
        self._update_queue()

    def add_chest_unlocked(self):
        """add chest unlocked to log"""
        self.chests_unlocked += 1
        if self.console_log:
            self.log_to_console()
        self._update_queue()

    def add_card_played(self):
        """add card played to log"""
        self.cards_played += 1
        if self.console_log:
            self.log_to_console()
        self._update_queue()

    def add_card_upgraded(self):
        """add card upgraded to log"""
        self.cards_upgraded += 1
        if self.console_log:
            self.log_to_console()
        self._update_queue()

    def add_account_switch(self):
        """add account switch to log"""
        self.account_switches += 1
        if self.console_log:
            self.log_to_console()
        self._update_queue()

    def add_win(self):
        """add win to log"""
        self.wins += 1
        if self.console_log:
            self.log_to_console()
        self._update_queue()

    def add_loss(self):
        """add loss to log"""
        self.losses += 1
        if self.console_log:
            self.log_to_console()
        self._update_queue()

    def add_fight(self):
        """add fight to log"""
        self.fights += 1
        if self.console_log:
            self.log_to_console()
        self._update_queue()

    def add_request(self):
        """add request to log"""
        self.requests += 1
        if self.console_log:
            self.log_to_console()
        self._update_queue()

    def add_restart(self):
        """add restart to log"""
        self.restarts += 1
        if self.console_log:
            self.log_to_console()
        self._update_queue()

    def change_status(self, status):
        """change status of bot in log

        Args:
            status (str): status of bot
        """
        self.current_status = status
        if self.console_log:
            self.log_to_console()
        self._update_queue()
