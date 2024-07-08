import sys
from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QTabWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QCheckBox,
    QSpinBox,
    QPushButton,
    QTableWidget,
    QSizePolicy,
    QTableWidgetItem,
    QHeaderView,
)
from pyclashbot.interface.layout_data import (
    botStatsDict,
    battleStatsDict,
    collectionStatsDict,
    tabName2jobList,
    JOB_DEFAULT_STATES,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from pyclashbot.interface.pyqt_themes import THEMES

theme = THEMES["midnight_blue_theme"]


class FrontEnd(QWidget):
    start_button_pressed = Signal()  # Custom signal

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Py-ClashBot")
        self.resize(800, 600)  # Set the window size to 800x600

        # Top layout for title and buttons
        top_layout = QHBoxLayout()

        # Add title text
        title_label = QLabel("Py-ClashBot")
        title_font = QFont("Arial", 24, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_layout.addWidget(title_label)

        # Add buttons
        buttons_layout = QHBoxLayout()

        # Add Discord button
        discord_button = QPushButton("Discord")
        discord_color = QColor(114, 137, 218)  # Discord's blue-purple hue
        discord_button.setStyleSheet(
            f"background-color: {discord_color.lighter(150).name()}; color: white; font-size: 16px; padding: 10px;"
        )
        discord_button.setFixedSize(100, 50)
        discord_button.clicked.connect(lambda: self.print_button_pressed("Discord"))
        buttons_layout.addWidget(discord_button)

        # Add START button
        start_button = QPushButton("START")
        start_button.setStyleSheet(
            "background-color: #9ACD32; color: white; font-size: 16px; padding: 10px;"
        )  # Pastel green
        start_button.setFixedSize(100, 50)
        start_button.clicked.connect(self.start_button_clicked)
        buttons_layout.addWidget(start_button)

        # Add Bug Report button
        bug_report_button = QPushButton("Bug Report")
        bug_report_button.setStyleSheet(
            "background-color: #FF6347; color: white; font-size: 16px; padding: 10px;"
        )  # Pastel red
        bug_report_button.setFixedSize(100, 50)
        bug_report_button.clicked.connect(
            lambda: self.print_button_pressed("Bug Report")
        )
        buttons_layout.addWidget(bug_report_button)

        # Add Upload Log button
        upload_log_button = QPushButton("Upload Log")
        upload_log_button.setStyleSheet(
            "background-color: #87CEFA; color: white; font-size: 16px; padding: 10px;"
        )  # Pastel blue
        upload_log_button.setFixedSize(100, 50)
        upload_log_button.clicked.connect(
            lambda: self.print_button_pressed("Upload Log")
        )
        buttons_layout.addWidget(upload_log_button)

        # Add buttons layout to top layout
        top_layout.addLayout(buttons_layout)

        # Main layout for the entire window
        main_layout = QVBoxLayout()

        # Add top layout (title and buttons) to main layout
        main_layout.addLayout(top_layout)

        # Create a tab widget
        tab_widget = QTabWidget()

        # Create first tab (General Settings)
        tab1 = QWidget()
        general_settings_tab_layout = QVBoxLayout()

        # Add placeholder text
        placeholder_text = QLabel(
            "This is placeholder text. This is placeholder text. This is placeholder text. "
            "This is placeholder text. This is placeholder text. This is placeholder text."
        )
        placeholder_text.setWordWrap(True)
        general_settings_tab_layout.addWidget(placeholder_text)

        # Add 'enable docking' checkbox
        self.enable_docking_checkbox = QCheckBox("Enable docking")
        general_settings_tab_layout.addWidget(self.enable_docking_checkbox)

        # Add 'enable analytics' checkbox
        self.enable_analytics_checkbox = QCheckBox("Enable Analytics")
        general_settings_tab_layout.addWidget(self.enable_analytics_checkbox)

        tab1.setLayout(general_settings_tab_layout)

        # Create second tab (Bot Settings)
        bot_settings_tab = QWidget()
        bot_settings_layout = QVBoxLayout()
        bot_settings_page_text = QLabel("Stuff to show on bot settings page")
        bot_settings_layout.addWidget(bot_settings_page_text)

        self.nested_tab_widget = QTabWidget()
        self.nested_tab_bar = self.nested_tab_widget.tabBar()

        # Create nested tabs
        self.create_nested_tabs()

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

        bot_settings_layout.addWidget(self.nested_tab_widget)
        bot_settings_tab.setLayout(bot_settings_layout)

        tab_widget.addTab(tab1, "General Settings")
        tab_widget.addTab(bot_settings_tab, "Bot Settings")

        # Create third tab (Runtime Statistics)
        runtime_stats_tab = QWidget()
        runtime_stats_layout = QVBoxLayout()
        runtime_stats_page_text = QLabel("Stuff to show on runtime statistics page")
        runtime_stats_layout.addWidget(runtime_stats_page_text)

        # Add table widget to display bot stats
        self.bot_stats_table = QTableWidget()
        self.bot_stats_table.setColumnCount(2)
        self.bot_stats_table.setRowCount(len(botStatsDict))
        self.bot_stats_table.setHorizontalHeaderLabels(["Stat", "Value"])
        self.bot_stats_table.horizontalHeader().setStretchLastSection(True)
        self.bot_stats_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.bot_stats_table.verticalHeader().setVisible(False)
        self.bot_stats_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.bot_stats_table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Populate bot stats table with initial data
        self.populate_stats_table(self.bot_stats_table, botStatsDict)
        runtime_stats_layout.addWidget(self.bot_stats_table)

        # Add table widget to display battle stats
        self.battle_stats_table = QTableWidget()
        self.battle_stats_table.setColumnCount(2)
        self.battle_stats_table.setRowCount(len(battleStatsDict))
        self.battle_stats_table.setHorizontalHeaderLabels(["Stat", "Value"])
        self.battle_stats_table.horizontalHeader().setStretchLastSection(True)
        self.battle_stats_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.battle_stats_table.verticalHeader().setVisible(False)
        self.battle_stats_table.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        self.battle_stats_table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Populate battle stats table with initial data
        self.populate_stats_table(self.battle_stats_table, battleStatsDict)
        runtime_stats_layout.addWidget(self.battle_stats_table)

        # Add table widget to display collection stats
        self.collection_stats_table = QTableWidget()
        self.collection_stats_table.setColumnCount(2)
        self.collection_stats_table.setRowCount(len(collectionStatsDict))
        self.collection_stats_table.setHorizontalHeaderLabels(["Stat", "Value"])
        self.collection_stats_table.horizontalHeader().setStretchLastSection(True)
        self.collection_stats_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.collection_stats_table.verticalHeader().setVisible(False)
        self.collection_stats_table.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        self.collection_stats_table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Populate collection stats table with initial data
        self.populate_stats_table(self.collection_stats_table, collectionStatsDict)
        runtime_stats_layout.addWidget(self.collection_stats_table)

        runtime_stats_tab.setLayout(runtime_stats_layout)
        tab_widget.addTab(runtime_stats_tab, "Runtime Statistics")

        main_layout.addWidget(tab_widget)
        self.setLayout(main_layout)

    def print_button_pressed(self, button_name):
        print(f"{button_name} button pressed")

    def start_button_clicked(self):
        print("Start button clicked!")
        self.start_button_pressed.emit()  # Emit the custom signal

    def create_nested_tabs(self):
        for tab_name, job_list in tabName2jobList.items():
            nested_tab = QWidget()
            nested_tab_layout = QVBoxLayout()

            for job_name, toggle_name, increment_name in job_list:
                job_toggle_checkbox = QCheckBox(job_name)
                job_toggle_checkbox.setObjectName(toggle_name)
                job_toggle_checkbox.setChecked(JOB_DEFAULT_STATES.get(job_name, False))
                nested_tab_layout.addWidget(job_toggle_checkbox)

                if increment_name:
                    job_spin_box = QSpinBox()
                    job_spin_box.setObjectName(increment_name)
                    job_spin_box.setValue(JOB_DEFAULT_STATES.get(job_name, 0))
                    nested_tab_layout.addWidget(job_spin_box)

            nested_tab.setLayout(nested_tab_layout)
            self.nested_tab_widget.addTab(nested_tab, tab_name)

    def populate_stats_table(self, table_widget, stats_dict):
        row = 0
        for stat, value in stats_dict.items():
            stat_item = QTableWidgetItem(stat)
            value_item = QTableWidgetItem(str(value))
            table_widget.setItem(row, 0, stat_item)
            table_widget.setItem(row, 1, value_item)
            row += 1

    def add_new_tab(self):
        # Example of adding a new tab dynamically
        new_tab = QWidget()
        new_tab_layout = QVBoxLayout()
        new_tab_label = QLabel("New Tab Content")
        new_tab_layout.addWidget(new_tab_label)
        new_tab.setLayout(new_tab_layout)
        self.nested_tab_widget.addTab(new_tab, "New Tab")
