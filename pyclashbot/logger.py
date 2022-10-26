import time


class Logger:
    """Handles creating and reading logs
    """

    def __init__(self):
        """Logger init
        """
        self.start_time = time.time()
        self.wins = 0
        self.losses = 0
        self.fights = 0
        self.requests = 0
        self.restarts = 0

        self.chests_unlocked = 0
        self.cards_played = 0
        self.cards_upgraded = 0
        self.account_switches = 0

        self.current_status = "Starting"
        self.buffer = ""

    def make_timestamp(self):
        """creates a time stamp for log output

        Returns:
            str: log time stamp
        """
        output_time = time.time() - self.start_time
        output_time = int(output_time)

        return str(self.convert_int_to_time(output_time))

    def make_score_board(self):
        """creates scoreboard for log output

        Returns:
            str: log scoreboard
        """
        losses_str = f"{str(self.losses)}L"
        wins_str = f"{str(self.wins)}W"
        return f"{wins_str}|{losses_str}"

    def convert_int_to_time(self, seconds):
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

    def log(self):
        """log to console"""

        self.add_row(
            "-----------------------------------------------------------------------------------")
        self.add_row(f"|      Program uptime:      | {self.make_timestamp()}")
        self.add_row(
            "|----------------------------------------------------------------------------------")
        self.add_row(f"|     Program restarts:     | {self.restarts}")
        self.add_row(
            "|----------------------------------------------------------------------------------")
        self.add_row(f"|         Requests:         | {self.requests}")
        self.add_row(
            "|----------------------------------------------------------------------------------")
        self.add_row(f"|          Fights:          | {self.fights}")
        self.add_row(
            "|----------------------------------------------------------------------------------")
        self.add_row(
            f"|         Win rate:         | {self.make_score_board()}")
        self.add_row(
            "|----------------------------------------------------------------------------------")
        self.add_row(f"|      Chests unlocked:     | {self.chests_unlocked}")
        self.add_row(
            "|----------------------------------------------------------------------------------")
        self.add_row(f"|       Cards played:       | {self.cards_played}")
        self.add_row(
            "|----------------------------------------------------------------------------------")
        self.add_row(f"|      Account switches:    | {self.account_switches}")
        self.add_row(
            "|----------------------------------------------------------------------------------")
        self.add_row(f"|      Current status:      | {self.current_status}")
        self.add_row(
            "-----------------------------------------------------------------------------------")
        self.print_buffer()

    def line_wrap(self, line: str, width: int) -> str:
        """wrap line to width

        Args:
            line (str): line to wrap
            width (int): width to wrap line to

        Returns:
            str: wrapped line
        """

        new_line = '\n|                           | '

        # split line into words
        words = line.split(' ')

        # wrap line
        wrapped_line = ''
        current_line = ''
        for word in words:
            if len(current_line) + len(word) < width:
                current_line += f'{word} '
            else:
                wrapped_line += current_line + new_line
                current_line = f'{word} '

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
            self.buffer += row + "\n"

    def print_buffer(self):
        """print log buffer"""
        print(self.buffer)
        self.buffer = ""  # clear buffer

    def add_chest_unlocked(self):
        """add chest unlocked to log"""
        self.chests_unlocked += 1
        self.log()

    def add_card_played(self):
        """add card played to log"""
        self.cards_played += 1
        self.log()

    def add_card_upgraded(self):
        """add card upgraded to log"""
        self.cards_upgraded += 1
        self.log()

    def add_account_switch(self):
        """add account switch to log"""
        self.account_switches += 1
        self.log()

    def add_win(self):
        """add win to log
        """
        self.wins += 1
        self.log()

    def add_loss(self):
        """add loss to log
        """
        self.losses += 1
        self.log()

    def add_fight(self):
        """add fight to log
        """
        self.fights += 1
        self.log()

    def add_request(self):
        """add request to log"""
        self.requests += 1
        self.log()

    def add_restart(self):
        """add restart to log"""
        self.restarts += 1
        self.log()

    def change_status(self, status):
        """change status of bot in log

        Args:
            status (str): status of bot
        """
        self.current_status = status
        self.log()
