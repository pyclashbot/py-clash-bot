"""pysimplegui layout for stats tab"""
import PySimpleGUI as sg
from PySimpleGUI.PySimpleGUI import Text
from pyclashbot.interface.theme import THEME

sg.theme(THEME)


def stat_box(stat_name: str, size=(5, 1)) -> sg.Text:
    """Returns a pysimplegui text box object for stats layout"""
    return sg.Text(
        "0",
        key=stat_name,
        relief=sg.RELIEF_SUNKEN,
        text_color="blue",
        size=size,
    )


# collection stats

collection_stats_titles: list[list[Text]] = [
    [
        sg.Text("Requests: "),
    ],
    [
        sg.Text("Donates: "),
    ],
    [
        sg.Text("Chests Unlocked: "),
    ],
    [
        sg.Text("Card Mastery Rewards: "),
    ],
    [
        sg.Text("Cards Upgraded: "),
    ],
    [
        sg.Text("Free Offer Collects"),
    ],
]

collection_stats_values: list[list[Text]] = [
    [
        stat_box("requests"),
    ],
    [
        stat_box("donates"),
    ],
    [
        stat_box("chests_unlocked"),
    ],
    [
        stat_box("card_mastery_reward_collections"),
    ],
    [
        stat_box("upgrades"),
    ],
    [
        stat_box("free_offer_collections"),
    ],
]

collection_stats = [
    [
        sg.Column(collection_stats_titles, element_justification="right"),
        sg.Column(collection_stats_values, element_justification="left"),
    ]
]


# fight stats

battle_stats_titles: list[list[sg.Text]] = [
    [
        sg.Text("Wins: "),
    ],
    [
        sg.Text("Losses: "),
    ],
    [
        sg.Text("Friendly crowns: "),
    ],
    [
        sg.Text("Enemy crowns: "),
    ],
    [
        sg.Text("Win Rate: "),
    ],
    [
        sg.Text("Cards Played: "),
    ],
    [
        sg.Text("1v1 Fights: "),
    ],
    [
        sg.Text("2v2 Fights: "),
    ],
    [
        sg.Text("War Fights: "),
    ],
    [
        sg.Text("Card Swaps: "),
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
        stat_box("friendly_crowns"),
    ],
    [
        stat_box("enemy_crowns"),
    ],
    [
        stat_box("winrate"),
    ],
    [
        stat_box("cards_played"),
    ],
    [
        stat_box("1v1_fights"),
    ],
    [
        stat_box("2v2_fights"),
    ],
    [
        stat_box("war_fights"),
    ],
    [
        stat_box("card_randomizations"),
    ],
]

battle_stats = [
    [
        sg.Column(battle_stats_titles, element_justification="right"),
        sg.Column(battle_stats_values, element_justification="left"),
    ]
]


# bot stats

bot_stats_titles: list[list[sg.Text]] = [
    [
        sg.Text("Bot Failures"),
    ],
    [
        sg.Text("Runtime"),
    ],
]

bot_stats_values = [
    [
        stat_box("restarts_after_failure"),
    ],
    [
        stat_box("time_since_start", size=(7, 1)),
    ],
]

bot_stats = [
    [
        sg.Column(bot_stats_titles, element_justification="right"),
        sg.Column(bot_stats_values, element_justification="left"),
    ],
]
