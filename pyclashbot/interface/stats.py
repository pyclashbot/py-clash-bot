import PySimpleGUI as sg

from pyclashbot.interface.theme import THEME

sg.theme(THEME)


def stat_box(stat_name: str):
    return sg.Text(
        "0",
        key=stat_name,
        relief=sg.RELIEF_SUNKEN,
        text_color="blue",
        size=(5, 1),
    )


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
        sg.Text("2v2 Fights: "),
    ],
    [
        sg.Text("War Battles Fought: "),
    ],
]

battle_stats_values = [
    [
        stat_box("wins"),
    ],
    [
        stat_box("losses"),
    ],
    [
        stat_box("cards_played"),
    ],
    [
        stat_box("fights"),
    ],
    [
        stat_box("war_battles_fought"),
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
        stat_box("requests"),
    ],
    [
        stat_box("chests_unlocked"),
    ],
    [
        stat_box("cards_upgraded"),
    ],
    [
        stat_box("account_switches"),
    ],
    [
        stat_box("restarts"),
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
        stat_box("card_mastery_reward_collections"),
    ],
    [
        stat_box("battlepass_rewards_collections"),
    ],
    [
        stat_box("level_up_chest_collections"),
    ],
]

collections_stats = [
    [
        sg.Column(collections_stats_titles, element_justification="right"),
        sg.Column(collections_stats_values, element_justification="left"),
    ]
]
