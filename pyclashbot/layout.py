import sys

import PySimpleGUI as sg

sg.theme("SystemDefaultForReal")


def show_clash_royale_setup_gui():
    # a method to notify the user that clashroayle is not installed or setup

    out_text = """Clash Royale is not installed or setup.\nPlease install Clash Royale, finish the in-game tutorial\nand login before using this bot."""

    layout = [
        [sg.Text(out_text)],
    ]
    window = sg.Window("Clash Royale Not Setup!", layout)
    while True:
        read = window.read()
        if read is None:
            break
        event, values = read
        if event in [sg.WIN_CLOSED]:
            break
    window.close()
    sys.exit(0)


def show_help_gui():
    # Method for the secondary popup help gui for when the help button is
    # pressed

    out_text = """Py-ClashBot is a bot that can be used to automate the process of playing
Clash Royale. It can be used to farm gold, upgrade cards, and much more.

To start the bot, select the jobs you want to run, set the number of accounts you want to use, and click start.

To stop the bot, click the stop button.

Click the 'Issues?' link to report any issues you may have with the bot."""

    layout = [
        [sg.Text(out_text)],
        [sg.Button("Exit")],
    ]
    window = sg.Window("Help", layout)
    while True:
        read = window.read()
        if read is None:
            break
        event, values = read
        if event in [sg.WIN_CLOSED, "Exit"]:
            break
    window.close()


battle_stats_title = [
    [
        sg.Text("Wins: "),
    ],
    [
        sg.Text("Losses: "),
    ],
    [
        sg.Text("Cards Played: "),
    ],
    [
        sg.Text("Fights: "),
    ],
    [
        sg.Text("War Battles Fought: "),
    ],
]

battle_stats_values = [
    [
        sg.Text(
            "0",
            key="wins",
            relief=sg.RELIEF_SUNKEN,
            text_color="blue",
            size=(5, 1),
        ),
    ],
    [
        sg.Text(
            "0",
            key="losses",
            relief=sg.RELIEF_SUNKEN,
            text_color="blue",
            size=(5, 1),
        ),
    ],
    [
        sg.Text(
            "0",
            key="restarts",
            relief=sg.RELIEF_SUNKEN,
            text_color="blue",
            size=(5, 1),
        ),
    ],
    [
        sg.Text(
            "0",
            key="fights",
            relief=sg.RELIEF_SUNKEN,
            text_color="blue",
            size=(5, 1),
        ),
    ],
    [
        sg.Text(
            "0",
            key="war_battles_fought",
            relief=sg.RELIEF_SUNKEN,
            text_color="blue",
            size=(5, 1),
        ),
    ],
]

battle_stats = [
    [
        sg.Column(battle_stats_title, element_justification="right"),
        sg.Column(battle_stats_values, element_justification="left"),
    ]
]

progress_stats_titles = [
    [
        sg.Text("Requests: "),
    ],
    [
        sg.Text("Chests Unlocked: "),
    ],
    [
        sg.Text("Cards Upgraded: "),
    ],
    [
        sg.Text("Account Switches: "),
    ],
    [
        sg.Text("Restarts: "),
    ],
]

progress_stats_values = [
    [
        sg.Text(
            "0",
            key="requests",
            relief=sg.RELIEF_SUNKEN,
            text_color="blue",
            size=(5, 1),
        ),
    ],
    [
        sg.Text(
            "0",
            key="chests_unlocked",
            relief=sg.RELIEF_SUNKEN,
            text_color="blue",
            size=(5, 1),
        ),
    ],
    [
        sg.Text(
            "0",
            key="cards_played",
            relief=sg.RELIEF_SUNKEN,
            text_color="blue",
            size=(5, 1),
        ),
    ],
    [
        sg.Text(
            "0",
            key="cards_upgraded",
            relief=sg.RELIEF_SUNKEN,
            text_color="blue",
            size=(5, 1),
        ),
    ],
    [
        sg.Text(
            "0",
            key="account_switches",
            relief=sg.RELIEF_SUNKEN,
            text_color="blue",
            size=(5, 1),
        ),
    ],
]

progress_stats = [
    [
        sg.Column(progress_stats_titles, element_justification="right"),
        sg.Column(progress_stats_values, element_justification="left"),
    ]
]

collections_stats_titles = [
    [
        sg.Text(
            "Card Mastery Reward Collections: ",
        ),
    ],
    [
        sg.Text("Battlepass Reward Collections: "),
    ],
    [
        sg.Text("Level Up Chest Collections: "),
    ],
]

collections_stats_values = [
    [
        sg.Text(
            "0",
            key="card_mastery_reward_collections",
            relief=sg.RELIEF_SUNKEN,
            text_color="blue",
            size=(5, 1),
        ),
    ],
    [
        sg.Text(
            "0",
            key="battlepass_rewards_collections",
            relief=sg.RELIEF_SUNKEN,
            text_color="blue",
            size=(5, 1),
        ),
    ],
    [
        sg.Text(
            "0",
            key="level_up_chest_collections",
            relief=sg.RELIEF_SUNKEN,
            text_color="blue",
            size=(5, 1),
        ),
    ],
]

collections_stats = [
    [
        sg.Column(collections_stats_titles, element_justification="right"),
        sg.Column(collections_stats_values, element_justification="left"),
    ]
]

jobs_checklist = [
    [
        sg.Column(
            [
                [
                    sg.Checkbox(
                        "Open chests",
                        default=True,
                        key="-Open-Chests-in-",
                        enable_events=True,
                    ),
                ],
                [
                    sg.Checkbox(
                        "Fight",
                        default=True,
                        key="-Fight-in-",
                        enable_events=True,
                    ),
                ],
                [
                    sg.Checkbox(
                        "Random Requesting",
                        default=True,
                        key="-Requesting-in-",
                        enable_events=True,
                    ),
                ],
                [
                    sg.Checkbox(
                        "Upgrade cards",
                        default=True,
                        key="-Upgrade_cards-in-",
                        enable_events=True,
                    ),
                ],
                [
                    sg.Checkbox(
                        "War Participation",
                        default=True,
                        key="-War-Participation-in-",
                        enable_events=True,
                    ),
                ],
                [
                    sg.Checkbox(
                        "Random decks",
                        default=True,
                        key="-Random-Decks-in-",
                        enable_events=True,
                    ),
                ],
                [
                    sg.Checkbox(
                        "Card Mastery Collection",
                        default=True,
                        key="-Card-Mastery-Collection-in-",
                        enable_events=True,
                    ),
                ],
                [
                    sg.Checkbox(
                        "Level Up Reward Collection",
                        default=True,
                        key="-Level-Up-Reward-Collection-in-",
                        enable_events=True,
                    ),
                ],
                [
                    sg.Checkbox(
                        "Battlepass Reward Collection",
                        default=True,
                        key="-Battlepass-Reward-Collection-in-",
                        enable_events=True,
                    ),
                ],
            ],
            scrollable=True,
            vertical_scroll_only=True,
            expand_x=True,
            size=(None, 90),
        )
    ],
]

controls = [
    [
        sg.Column(
            [
                [
                    sg.Button("Start"),
                    sg.Button("Stop", disabled=True),
                ],
                [
                    sg.Text("# of Accounts: "),
                    sg.Combo(
                        ["1", "2", "3", "4"],
                        key="-SSID_IN-",
                        default_value="1",
                        enable_events=True,
                    ),
                ],
                [
                    sg.Button("Help"),
                    sg.Button("Donate"),
                ],
            ],
        ),
    ],
]

description = [
    [
        sg.Text("Matthew Miglio\nMartin Miglio\nOctober 2022\n", size=(13, None)),
    ],
    [
        sg.Text(
            "Issues?",
            key="issues-link",
            enable_events=True,
            tooltip="https://github.com/matthewmiglio/py-clash-bot/issues/new/choose",
            text_color="blue",
        ),
    ],
]

layout = [
    [
        sg.Frame(layout=jobs_checklist, title="Jobs"),
        sg.Frame(layout=controls, title="Controls"),
    ],
    [
        sg.Frame(
            layout=battle_stats,
            title="Battle Stats",
        ),
        sg.Frame(
            layout=progress_stats,
            title="Progress Stats",
        ),
    ],
    [
        sg.Frame(
            layout=collections_stats,
            title="Collection Stats",
        ),
        sg.Frame(
            layout=description,
            title="Info",
        ),
    ],
    [
        sg.Text("Current Status: "),
        sg.InputText(
            "Idle",
            key="current_status",
            use_readonly_for_disable=True,
            disabled=True,
            text_color="blue",
            size=(40, 1),
        ),
    ],
]

# a list of all the keys that contain user configuration
user_config_keys = [
    "-SSID_IN-",
    "-Open-Chests-in-",
    "-Fight-in-",
    "-Requesting-in-",
    "-Upgrade_cards-in-",
    "-War-Participation-in-",
    "-Random-Decks-in-",
    "-Card-Mastery-Collection-in-",
    "-Level-Up-Reward-Collection-in-",
    "-Battlepass-Reward-Collection-in-",
]

# list of button and checkbox keys to disable when the bot is running
disable_keys = user_config_keys + ["Start"]


# a dummy test function to simulate the bot running
if __name__ == "__main__":
    import time
    import webbrowser
    from typing import Any

    # some sample statistics
    statistics: dict[str, Any] = {
        "wins": 1,
        "losses": 2,
        "fights": 3,
        "requests": 4,
        "restarts": 5,
        "chests_unlocked": 6,
        "cards_played": 7,
        "cards_upgraded": 8,
        "account_switches": 9,
        "card_mastery_reward_collections": 10,
        "battlepass_rewards_collections": 11,
        "level_up_chest_collections": 12,
        "war_battles_fought": 13,
        "current_status": "Starting",
    }

    window = sg.Window("Statistics", layout)

    running = False

    while True:
        event, values = window.read(timeout=100)  # type: ignore
        if event == sg.WIN_CLOSED:
            break
        elif event == "Start":
            window["current_status"].update("Starting")  # type: ignore
            for key in disable_keys:
                window[key].update(disabled=True)
            running = True
            window["Stop"].update(disabled=False)

        elif event == "Stop":
            window["current_status"].update("Stopping")  # type: ignore
            running = False
            for key in disable_keys:
                window[key].update(disabled=False)
            window["Stop"].update(disabled=True)

        elif event == "Help":
            show_help_gui()

        elif event == "Donate":
            webbrowser.open(
                "https://www.paypal.com/donate/?business=YE72ZEB3KWGVY&no_recurring=0&item_name=Support+my+projects%21&currency_code=USD"
            )

        elif event == "issues-link":
            webbrowser.open(
                "https://github.com/matthewmiglio/py-clash-bot/issues/new/choose"
            )

        if running:
            # change some of the statistics
            statistics["wins"] += 1
            statistics["losses"] += 1
            statistics["fights"] += 1
            statistics["war_battles_fought"] += 1
            statistics["requests"] += 1

        # update the statistics
        window["wins"].update(statistics["wins"])
        window["losses"].update(statistics["losses"])
        window["fights"].update(statistics["fights"])
        window["war_battles_fought"].update(statistics["war_battles_fought"])
        window["requests"].update(statistics["requests"])

        time.sleep(1)

    window.close()
