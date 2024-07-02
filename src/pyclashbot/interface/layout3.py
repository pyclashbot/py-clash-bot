import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QTabWidget,
    QVBoxLayout,
    QLabel,
    QCheckBox,
    QSpinBox,
    QHBoxLayout,
    QPushButton,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont  # Import QFont from PyQt6.QtGui
from pyclashbot.interface.pyqt_themes import THEMES

print("Available themes:")
for title, theme in THEMES.items():
    print(f"{title}")

theme = THEMES["midnight_blue_theme"]

# Constants defining initial checkbox states for each job
JOB_DEFAULT_STATES = {
    "Request": True,
    "Donate": False,
    "Buy shop offers": True,
    "Upgrade your deck": True,
    "Buy from the season shop": False,
    "Open chests": True,
    "Collect battlepass": False,
    "Colled card mastery": True,
    "Collect daily rewards": False,
    "Collect level up chest": True,
    "Collect Bannerbox": False,
    "Collect Trophy Rewards": True,
    "Fight trophy road battle": False,
    "Fight goblin queen battle": True,
    "Fight path of legends battle": False,
    "Fight 2v2 battle": True,
    "Fight war battle": False,
    "Randomize deck": True,
    "Random plays": False,
    "Disable win/loss tracking": True,
    "Skip fighting when full chests": False,
}


tabName2jobList = {
    "Card Jobs": [
        "Request",
        "Donate",
        "Buy shop offers",
        "Upgrade your deck",
        "Buy from the season shop",
    ],
    "Rewards Jobs": [
        "Open chests",
        "Collect battlepass",
        "Colled card mastery",
        "Collect daily rewards",
        "Collect level up chest",
        "Collect Bannerbox",
        "Collect Trophy Rewards",
    ],
    "Fight Jobs": [
        "Fight trophy road battle",
        "Fight goblin queen battle",
        "Fight path of legends battle",
        "Fight 2v2 battle",
        "Fight war battle",
        "Randomize deck",
        "Random plays",
        "Disable win/loss tracking",
        "Skip fighting when full chests",
    ],
}


class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("PyQt6 Tabs Example")
        self.resize(800, 600)  # Set the window size to 800x600

        layout = QVBoxLayout()

        tab_widget = QTabWidget()

        # Create first tab (General Settings)
        tab1 = QWidget()
        tab1_layout = QVBoxLayout()

        # Add title text
        title_text = QLabel(
            "This is placeholder text. This is placeholder text. This is placeholder text. "
            "This is placeholder text. This is placeholder text. This is placeholder text."
        )
        title_text.setWordWrap(True)
        tab1_layout.addWidget(title_text)

        # Add 'enable docking' checkbox
        enable_docking_checkbox = QCheckBox("Enable docking")
        tab1_layout.addWidget(enable_docking_checkbox)

        tab1.setLayout(tab1_layout)

        # Create second tab (Bot Settings)
        tab2 = QWidget()
        tab2_layout = QVBoxLayout()
        tab2_label = QLabel("Stuff to show on bot settings page")
        tab2_layout.addWidget(tab2_label)

        self.nested_tab_widget = QTabWidget()
        self.nested_tab_bar = self.nested_tab_widget.tabBar()

        # Create nested tabs
        self.create_nested_tab("Bot #1 Settings")
        self.create_nested_tab("Bot #2 Settings")
        self.create_nested_tab("Bot #3 Settings")

        # Add "plus" button to add new tabs
        self.plus_button = QPushButton("+")
        self.plus_button.setFixedSize(30, 30)
        self.plus_button.clicked.connect(self.add_new_tab)
        self.nested_tab_bar.setMovable(True)
        self.nested_tab_bar.setTabsClosable(False)
        self.nested_tab_bar.setExpanding(True)

        self.nested_tab_widget.setCornerWidget(
            self.plus_button, Qt.Corner.TopRightCorner
        )

        tab2_layout.addWidget(self.nested_tab_widget)
        tab2.setLayout(tab2_layout)

        # Create third tab (Runtime Statistics)
        tab3 = QWidget()
        tab3_layout = QVBoxLayout()
        tab3_label = QLabel("Stuff to show on statistics page")
        tab3_layout.addWidget(tab3_label)
        tab3.setLayout(tab3_layout)

        # Add tabs to the QTabWidget
        tab_widget.addTab(tab1, "General Settings")
        tab_widget.addTab(tab2, "Bot Settings")
        tab_widget.addTab(tab3, "Runtime Statistics")

        layout.addWidget(tab_widget)
        self.setLayout(layout)

        # Apply a dark theme
        self.setStyleSheet(theme)

    def create_nested_tab(self, title):
        nested_tab = QWidget()
        nested_tab_layout = QVBoxLayout()

        inner_tab_widget = QTabWidget()

        # Create tabs using tabName2jobList
        for tab_name, job_list in tabName2jobList.items():
            tab = QWidget()
            tab_layout = QVBoxLayout()
            tab_layout.addWidget(QLabel(f"Content of {tab_name}"))

            # Add job toggle inputs based on job_list
            for job_name in job_list:
                row_layout = QHBoxLayout()
                checkbox = QCheckBox("Enable")
                checkbox.setChecked(JOB_DEFAULT_STATES.get(job_name, False))
                checkbox.setFont(QFont("Arial", 10))  # Increase font size
                input_label = QLabel(f"{job_name} every")
                input_label.setFont(QFont("Arial", 10))  # Increase font size
                spin_box = QSpinBox()
                spin_box.setRange(1, 100)  # Example range
                battles_label = QLabel("battles")
                battles_label.setFont(QFont("Arial", 10))  # Increase font size

                # Align widgets in the row
                row_layout.addWidget(checkbox)
                row_layout.addWidget(input_label)
                row_layout.addWidget(spin_box)
                row_layout.addWidget(battles_label)
                row_layout.addStretch(1)  # Add stretch to align from the left

                tab_layout.addLayout(row_layout)

            tab.setLayout(tab_layout)
            inner_tab_widget.addTab(tab, tab_name)

        nested_tab_layout.addWidget(inner_tab_widget)
        nested_tab.setLayout(nested_tab_layout)
        self.nested_tab_widget.addTab(nested_tab, title)

    def add_new_tab(self):
        new_tab_index = self.nested_tab_widget.count() + 1
        self.create_nested_tab(f"Bot #{new_tab_index} Settings")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MyApp()
    ex.show()
    sys.exit(app.exec())
