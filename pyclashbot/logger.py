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

        self.current_status = "Idle"

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

        time_str = self.make_timestamp()
        restarts_str = f"{str(self.restarts)}"
        requests_str = f"{str(self.requests)}"
        fights_str = f"{str(self.fights)}"
        win_loss_str = self.make_score_board()
        chests_unlocked_str = f"{str(self.chests_unlocked)}"
        cards_played_str = f"{str(self.cards_played)}"
        account_switches_str = f"{str(self.account_switches)}"
        status_str = self.current_status

        print("-----------------------------------------------------------------------------------")
        print(f"|      Program uptime:      | {time_str}")
        print("|----------------------------------------------------------------------------------")
        print(f"|     Program restarts:     | {restarts_str}")
        print("|----------------------------------------------------------------------------------")
        print(f"|         Requests:         | {requests_str}")
        print("|----------------------------------------------------------------------------------")
        print(f"|          Fights:          | {fights_str}")
        print("|----------------------------------------------------------------------------------")
        print(f"|         Win rate:         | {win_loss_str}")
        print("|----------------------------------------------------------------------------------")
        print(f"|      Chests unlocked:     | {chests_unlocked_str}")
        print("|----------------------------------------------------------------------------------")
        print(f"|       Cards played:       | {cards_played_str}")
        print("|----------------------------------------------------------------------------------")
        print(f"|      Account switches:    | {account_switches_str}")
        print("|----------------------------------------------------------------------------------")
        print(f"|      Current status:      | {status_str}")
        print("-----------------------------------------------------------------------------------")

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
