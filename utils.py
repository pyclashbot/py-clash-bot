import time


class Logger:
    def __init__(self):
        self.start_time = time.time()
        self.wins = 0
        self.losses = 0
        self.fights = 0

    def make_timestamp(self):
        output_time = time.time()-self.start_time
        output_time = int(output_time)

        time_str = str(self.convert_int_to_time(output_time))
        wins_str = str(self.wins)+"W"
        losses_str = str(self.losses)+"L"
        gap_str = "|"
        output_string = time_str+gap_str+wins_str+gap_str+losses_str+": "

        return output_string

    def convert_int_to_time(self, seconds):
        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        return "%d:%02d:%02d" % (hour, minutes, seconds)

    def log(self, message):
        print(self.make_timestamp(), message)

    def add_win(self):
        self.wins += 1

    def add_loss(self):
        self.losses += 1

    def add_fight(self):
        self.fights += 1