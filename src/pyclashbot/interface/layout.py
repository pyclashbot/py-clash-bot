from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QCheckBox,
    QLabel,
)


class Layout(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # wins label
        wins_layout = QHBoxLayout()
        wins_label = QLabel("Wins:")
        wins_layout.addWidget(wins_label)

        #wins textbox
        self.wins_textbox = QLineEdit()
        self.wins_textbox.setReadOnly(True)
        self.wins_textbox.setText("0")
        wins_layout.addWidget(self.wins_textbox)

        #add wins stat to layout
        main_layout.addLayout(wins_layout)

        #label for losses
        losses_layout = QHBoxLayout()
        losses_label = QLabel("Losses:")
        losses_layout.addWidget(losses_label)

        #textbox 
        self.losses_textbox = QLineEdit()
        self.losses_textbox.setReadOnly(True)
        self.losses_textbox.setText("0")
        losses_layout.addWidget(self.losses_textbox)

        main_layout.addLayout(losses_layout)

        self.start_button = QPushButton("Start")
        main_layout.addWidget(self.start_button)

        # Add checkboxes for various functionalities
        self.checkboxes = {}
        checkbox_names = [
            "Trophy road 1v1 fights",
            "Queens journey 1v1 fights",
            "Path of legends 1v1 fights",
            "2v2 fights",
        ]

        for name in checkbox_names:
            checkbox = QCheckBox(name)
            main_layout.addWidget(checkbox)
            self.checkboxes[name] = checkbox

    def get_checkboxes(self):
        checkboxes_state = {}
        for name, checkbox in self.checkboxes.items():
            checkboxes_state[name] = checkbox.isChecked()
        return checkboxes_state
