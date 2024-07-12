import sys
from pyclashbot.interface.layout import Layout
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Signal, QObject


class Stats(QObject):
    update_signal = Signal(int)

    def __init__(self, window):
        super().__init__()
        self.wins = 0
        self.losses = 0
        self.window = window
        self.update_signal.connect(self.update_window)

    def increment_wins(self):
        self.wins += 1
        self.update_window()

    def increment_losses(self):
        self.losses += 1
        self.update_window()

    def update_window(self):
        self.window.losses_textbox.setText(str(self.losses))  # update losses
        self.window.wins_textbox.setText(str(self.wins))  # update wins


app = QApplication(sys.argv)
window = Layout()
stats = Stats(window)
