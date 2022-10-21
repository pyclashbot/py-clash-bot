import time
from turtle import window_height

from client import clear_log


class Logger:
    """Handles creating and reading logs
    """

    #initialize logger obj
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
        
    #Method to get current time as a readable string
    def make_timestamp(self):
        """creates a time stamp for log output

        Returns:
            str: log time stamp
        """
        output_time = time.time() - self.start_time
        output_time = int(output_time)

        return str(self.convert_int_to_time(output_time))

    #Method to make the win/loss string
    def make_score_board(self):
        """creates scoreboard for log output

        Returns:
            str: log scoreboard
        """
        losses_str = f"{str(self.losses)}L"
        wins_str = f"{str(self.wins)}W"
        return f"{wins_str}|{losses_str}"

    #Method to convert int to readable time string
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

    #Method to clear previous log and write new log
    def log(self):
        clear_log()
        gap_string = "|"
        time_str = self.make_timestamp() 
        restarts_str = f"{str(self.restarts)}"
        requests_str=f"{str(self.requests)}"
        fights_str=f"{str(self.fights)}"
        win_loss_str = self.make_score_board()
        chests_unlocked_str=f"{str(self.chests_unlocked)}"
        cards_played_str=f"{str(self.cards_played)}"
        cards_upgraded_str=f"{str(self.cards_upgraded)}"
        account_switches_str=f"{str(self.account_switches)}"
        
        
        
        status_str = self.current_status
        
        
        
        
        
        print("--------------------------------------------------------")
        print("|      Program uptime:      | " + time_str)
        print("|-------------------------------------------------------")
        print("|     Program restarts:     | " + restarts_str)
        print("|-------------------------------------------------------")
        print("|         Requests:         |",requests_str)
        print("|-------------------------------------------------------")
        print("|          Fights:          |",fights_str)
        print("|-------------------------------------------------------")
        print("|         Win rate:         |",win_loss_str)
        print("|-------------------------------------------------------")
        print("|      Chests unlocked:     |",chests_unlocked_str)
        print("|-------------------------------------------------------")
        print("|       Cards played:       |",cards_played_str)
        print("|-------------------------------------------------------")
        print("|      Account switches:    |",account_switches_str)
        print("|-------------------------------------------------------")
        print("|      Current status:      |",status_str)
        print("--------------------------------------------------------")
        
    #Method to increment chest unlocks
    def add_chest_unlocked(self):
        self.chests_unlocked += 1
        self.log()
    
    #Method to increment cards played
    def add_card_played(self):
        self.cards_played += 1
        self.log()
        
    #Method to increment cards upgradeds
    def add_card_upgraded(self):
        self.cards_upgraded += 1
        self.log()
     
    #Method to increment account_switchs
    def add_account_switch(self):
        self.account_switches += 1
        self.log()
     
    #Method to increment wins
    def add_win(self):
        """add win to log
        """
        self.wins += 1
        self.log()

    #Method to increment losses
    def add_loss(self):
        """add loss to log
        """
        self.losses += 1
        self.log()

    #Method to increment fights
    def add_fight(self):
        """add fight to log
        """
        self.fights += 1
        self.log()
        
    #Method to increment requests
    def add_request(self):
        self.requests += 1
        self.log()
        
    #Method to increment restarts
    def add_restart(self):
        self.restarts += 1
        self.log()
        
    #Method to update the bot's status
    def change_status(self,status):
        self.current_status=status
        self.log()