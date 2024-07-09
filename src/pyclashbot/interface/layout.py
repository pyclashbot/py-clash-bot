from PySide6.QtCore import Qt, Slot
from pyclashbot.interface.layout_data import (
    botStatsDict,
    battleStatsDict,
    collectionStatsDict,
    tabName2jobList,
    JOB_DEFAULT_STATES,
)
from pyclashbot.interface.pyqt_themes import THEMES
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QTabWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QCheckBox,
    QSpinBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Slot
from pyclashbot.bot.event_dispatcher import event_dispatcher

from PySide6.QtGui import QFont, QColor

from pyclashbot.interface.pyqt_themes import THEMES

theme = THEMES["midnight_blue_theme"]


class FrontEnd(QWidget):

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Py-ClashBot")
        self.resize(800, 600)

        self.job_checkboxes = {}
        self.job_spinboxes = {}
        self.worker = None

        self.initUI()

        # Connect the signals from the event dispatcher to the slots
        event_dispatcher.update_stats.connect(self.update_stats)
        event_dispatcher.increment_stat.connect(self.increment_stat)
        event_dispatcher.overwrite_stat.connect(self.overwrite_stat)

    def initUI(self):
        self.setupTopLayout()
        self.setupTabWidget()
        self.setupRuntimeStatsTab()

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(self.topLayout)
        main_layout.addWidget(self.tabWidget)

    @Slot(dict)
    def update_stats(self, stats):
        for key, value in stats.items():
            if key in botStatsDict:
                botStatsDict[key] = value
                self.update_table(self.bot_stats_table, botStatsDict)
            elif key in battleStatsDict:
                battleStatsDict[key] = value
                self.update_table(self.battle_stats_table, battleStatsDict)
            elif key in collectionStatsDict:
                collectionStatsDict[key] = value
                self.update_table(self.collection_stats_table, collectionStatsDict)

    @Slot(str)
    def increment_stat(self, stat):
        if stat in botStatsDict:
            botStatsDict[stat] += 1
            self.update_table(self.bot_stats_table, botStatsDict)
        elif stat in battleStatsDict:
            battleStatsDict[stat] += 1
            self.update_table(self.battle_stats_table, battleStatsDict)
        elif stat in collectionStatsDict:
            collectionStatsDict[stat] += 1
            self.update_table(self.collection_stats_table, collectionStatsDict)

    @Slot(str, object)
    def overwrite_stat(self, stat, value):
        if stat in botStatsDict:
            botStatsDict[stat] = value
            self.update_table(self.bot_stats_table, botStatsDict)
        elif stat in battleStatsDict:
            battleStatsDict[stat] = value
            self.update_table(self.battle_stats_table, battleStatsDict)
        elif stat in collectionStatsDict:
            collectionStatsDict[stat] = value
            self.update_table(self.collection_stats_table, collectionStatsDict)

    def update_table(self, table_widget, stats_dict):
        table_widget.clearContents()
        self.populate_stats_table(table_widget, stats_dict)

    def populate_stats_table(self, table_widget, stats_dict):
        table_widget.setRowCount(len(stats_dict))
        for row, (stat, value) in enumerate(stats_dict.items()):
            stat_item = QTableWidgetItem(stat)
            value_item = QTableWidgetItem(str(value))
            table_widget.setItem(row, 0, stat_item)
            table_widget.setItem(row, 1, value_item)



    def setupTopLayout(self):
        self.topLayout = QHBoxLayout()

        self.addTitleLabel()
        self.addButtons()

    def addTitleLabel(self):
        title_label = QLabel("Py-ClashBot")
        title_font = QFont("Arial", 24, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.topLayout.addWidget(title_label)

    def addButtons(self):
        buttons_layout = QHBoxLayout()

        discord_button = self.createButton(
            "Discord",
            QColor(114, 137, 218).lighter(150).name(),
            self.onDiscordButtonClick,
        )
        start_button = self.createButton("START", "#9ACD32", self.start_button_clicked)
        bug_report_button = self.createButton(
            "Bug Report", "#FF6347", self.onBugReportButtonClick
        )
        upload_log_button = self.createButton(
            "Upload Log", "#87CEFA", self.onUploadLogButtonClick
        )

        buttons_layout.addWidget(discord_button)
        buttons_layout.addWidget(start_button)
        buttons_layout.addWidget(bug_report_button)
        buttons_layout.addWidget(upload_log_button)

        self.topLayout.addLayout(buttons_layout)

    def createButton(self, text, background_color, click_handler):
        button = QPushButton(text)
        button.setStyleSheet(
            f"background-color: {background_color}; color: white; font-size: 16px; padding: 10px;"
        )
        button.setFixedSize(100, 50)
        button.clicked.connect(click_handler)
        return button

    def onDiscordButtonClick(self):
        print("Discord button clicked!")

    def onBugReportButtonClick(self):
        print("Bug Report button clicked!")

    def onUploadLogButtonClick(self):
        print("Upload Log button clicked!")

    def setupTabWidget(self):
        self.tabWidget = QTabWidget()

        self.setupGeneralSettingsTab()
        self.setupBotSettingsTab()

    def setupGeneralSettingsTab(self):
        tab1 = QWidget()
        layout = QVBoxLayout(tab1)

        placeholder_text = QLabel(
            "This is placeholder text. This is placeholder text. This is placeholder text. "
            "This is placeholder text. This is placeholder text. This is placeholder text."
        )
        placeholder_text.setWordWrap(True)
        layout.addWidget(placeholder_text)

        self.enable_docking_checkbox = QCheckBox("Enable docking")
        layout.addWidget(self.enable_docking_checkbox)

        self.enable_analytics_checkbox = QCheckBox("Enable Analytics")
        layout.addWidget(self.enable_analytics_checkbox)

        self.tabWidget.addTab(tab1, "General Settings")

    def setupBotSettingsTab(self):
        bot_settings_tab = QWidget()
        layout = QVBoxLayout(bot_settings_tab)

        bot_settings_page_text = QLabel("Stuff to show on bot settings page")
        layout.addWidget(bot_settings_page_text)

        self.nested_tab_widget = QTabWidget()
        self.create_nested_job_list_tabs()

        layout.addWidget(self.nested_tab_widget)

        self.tabWidget.addTab(bot_settings_tab, "Bot Settings")

    def create_nested_job_list_tabs(self):
        for tab_name, job_list in tabName2jobList.items():
            nested_tab = QWidget()
            layout = QVBoxLayout(nested_tab)

            for job_name, toggle_name, increment_name in job_list:
                job_layout = QHBoxLayout()

                job_toggle_checkbox = QCheckBox(job_name)
                job_toggle_checkbox.setObjectName(toggle_name)
                job_toggle_checkbox.setChecked(JOB_DEFAULT_STATES.get(job_name, False))
                job_layout.addWidget(job_toggle_checkbox)
                self.job_checkboxes[job_name] = job_toggle_checkbox

                if increment_name:
                    job_spin_box = QSpinBox()
                    job_spin_box.setObjectName(increment_name)
                    job_spin_box.setValue(JOB_DEFAULT_STATES.get(job_name, 0))
                    job_layout.addWidget(job_spin_box)
                    self.job_spinboxes[job_name] = job_spin_box
                else:
                    placeholder_label = QLabel(" ")  # Adding a space as a placeholder
                    job_layout.addWidget(placeholder_label)

                layout.addLayout(job_layout)

            self.nested_tab_widget.addTab(nested_tab, tab_name)

    def setupRuntimeStatsTab(self):
        runtime_stats_tab = QWidget()
        layout = QVBoxLayout(runtime_stats_tab)

        self.bot_stats_layout, self.bot_stats_table = self.create_table_with_title(
            "Bot Stats", botStatsDict
        )
        self.battle_stats_layout, self.battle_stats_table = (
            self.create_table_with_title("Battle Stats", battleStatsDict)
        )
        self.collection_stats_layout, self.collection_stats_table = (
            self.create_table_with_title("Collection Stats", collectionStatsDict)
        )

        layout.addLayout(self.bot_stats_layout)
        layout.addSpacing(20)
        layout.addLayout(self.battle_stats_layout)
        layout.addSpacing(20)
        layout.addLayout(self.collection_stats_layout)

        self.tabWidget.addTab(runtime_stats_tab, "Runtime Statistics")

    def create_table_with_title(self, title, stats_dict):
        layout = QVBoxLayout()

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        table_widget = QTableWidget()
        table_widget.setColumnCount(2)
        table_widget.setRowCount(len(stats_dict))
        table_widget.setHorizontalHeaderLabels(["Stat", "Value"])
        table_widget.horizontalHeader().setStretchLastSection(True)
        table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table_widget.verticalHeader().setVisible(False)
        table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        table_widget.setEditTriggers(QTableWidget.NoEditTriggers)

        self.populate_stats_table(table_widget, stats_dict)
        layout.addWidget(table_widget)

        return layout, table_widget

    def populate_stats_table(self, table_widget, stats_dict):
        table_widget.setRowCount(len(stats_dict))
        for row, (stat, value) in enumerate(stats_dict.items()):
            stat_item = QTableWidgetItem(stat)
            value_item = QTableWidgetItem(str(value))
            table_widget.setItem(row, 0, stat_item)
            table_widget.setItem(row, 1, value_item)

    def start_button_clicked(self):
        print("start button clicked")
