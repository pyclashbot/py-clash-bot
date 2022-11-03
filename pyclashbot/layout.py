import PySimpleGUI as sg

sg.theme("SystemDefaultForReal")

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
                    sg.Checkbox("Open chests", default=True, key="-Open-Chests-in-"),
                ],
                [
                    sg.Checkbox("Fight", default=True, key="-Fight-in-"),
                ],
                [
                    sg.Checkbox(
                        "Random Requesting", default=True, key="-Requesting-in-"
                    ),
                ],
                [
                    sg.Checkbox(
                        "Upgrade cards", default=True, key="-Upgrade_cards-in-"
                    ),
                ],
                [
                    sg.Checkbox(
                        "War Participation",
                        default=True,
                        key="-War-Participation-in-",
                    ),
                ],
                [
                    sg.Checkbox("Random decks", default=True, key="-Random-Decks-in-"),
                ],
                [
                    sg.Checkbox(
                        "Card Mastery Collection",
                        default=True,
                        key="-Card-Mastery-Collection-in-",
                    ),
                ],
                [
                    sg.Checkbox(
                        "Level Up Reward Collection",
                        default=True,
                        key="-Level-Up-Reward-Collection-in-",
                    ),
                ],
                [
                    sg.Checkbox(
                        "Battlepass Reward Collection",
                        default=True,
                        key="-Battlepass-Reward-Collection-in-",
                    ),
                ],
            ],
            scrollable=True,
            vertical_scroll_only=True,
            expand_x=True,
            size=(None, 80),
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
                    sg.Combo(["1", "2", "3", "4"], key="-SSID_IN-", default_value="1"),
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
        sg.Text(
            "Matthew Miglio\nOctober 2022\n\nAutomated\nClash Royale", size=(13, None)
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
        sg.Text(
            "idle",
            key="current_status",
            relief=sg.RELIEF_SUNKEN,
            text_color="blue",
            size=(40, 1),
        ),
    ],
]

# list of button and checkbox keys to disable when the bot is running
disable_keys = [
    "Start",
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

if __name__ == "__main__":
    import time
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

    while True:
        event, values = window.read(timeout=100)  # type: ignore
        if event == sg.WIN_CLOSED:
            break

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
