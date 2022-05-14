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

    def make_timestamp(self):
        """creates a time stamp for log output

        Returns:
            str: log time stamp
        """
        output_time = time.time()-self.start_time
        output_time = int(output_time)

        time_str = str(self.convert_int_to_time(output_time))

        output_string = time_str

        return output_string

    def make_score_board(self):
        """creates scoreboard for log output

        Returns:
            str: log scoreboard
        """
        wins_str = str(self.wins)+"W"
        losses_str = str(self.losses)+"L"
        gap_str = "|"
        return wins_str + gap_str + losses_str

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

    def log(self, message):
        """add message to log

        Args:
            message (str): message to add
        """
        print(f"{self.make_timestamp()} - {self.make_score_board()} : {message}")

    def add_win(self):
        """add win to log
        """
        self.wins += 1

    def add_loss(self):
        """add loss to log
        """
        self.losses += 1

    def add_fight(self):
        """add fight to log
        """
        self.fights += 1
