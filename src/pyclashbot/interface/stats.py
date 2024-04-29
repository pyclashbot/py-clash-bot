"""pysimplegui layout for stats tab"""

import PySimpleGUI as sg
from pyclashbot.interface.theme import THEME

sg.theme(THEME)


def stat_box(stat_name: str, size=(4, 1)) -> sg.Text:
    """Returns a pysimplegui text box object for stats layout"""
    return sg.Text(
        "0",
        key=stat_name,
        relief=sg.RELIEF_SUNKEN,
        text_color="blue",
        size=size,
    )


# collection stats

collection_stats_titles: list[list[sg.Text]] = [
    [
        sg.Text("Requests: "),
    ],
    [
        sg.Text("Shop Buys: "),
    ],
    [
        sg.Text("Donates: "),
    ],
    [
        sg.Text("Chests Unlocked: "),
    ],
    [
        sg.Text("Daily Rewards: "),
    ],
    [
        sg.Text("Card Mastery Rewards: "),
    ],
    [
        sg.Text("Bannerbox Collects: "),
    ],
    [
        sg.Text("Cards Upgraded: "),
    ],
    [
        sg.Text("Shop Offers Collected:"),
    ],
    [
        sg.Text("Battlepass Reward Collects"),
    ],
    [
        sg.Text("Level Up Reward Collects"),
    ],
    [
        sg.Text("War Chest Collects"),
    ],
    [
        sg.Text("Season Shop Buys"),
    ],
]

collection_stats_values: list[list[sg.Text]] = [
    [
        stat_box("requests"),
    ],
    [
        stat_box("shop_buys"),
    ],
    [
        stat_box("donates"),
    ],
    [
        stat_box("chests_unlocked"),
    ],
    [
        stat_box("daily_rewards"),
    ],
    [
        stat_box("card_mastery_reward_collections"),
    ],
    [
        stat_box("bannerbox_collects"),
    ],
    [
        stat_box("upgrades"),
    ],
    [
        stat_box("shop_offer_collections"),
    ],
    [
        stat_box("battlepass_collects"),
    ],
    [
        stat_box("level_up_chest_collects"),
    ],
    [
        stat_box("war_chest_collects"),
    ],
    [
        stat_box("season_shop_buys"),
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
        sg.Text("Win Rate: "),
    ],
    [
        sg.Text("Cards Played: "),
    ],
    [
        sg.Text("Path of Legends Battles: "),
    ],
    [
        sg.Text("Trophy Road Battles: "),
    ],
    [
        sg.Text("2v2 Fights: "),
    ],
    [
        sg.Text("War Fights: "),
    ],
    [
        sg.Text("Random Decks: "),
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
        stat_box("winrate"),
    ],
    [
        stat_box("cards_played"),
    ],
    [
        stat_box("path_of_legends_1v1_fights"),
    ],
    [
        stat_box("trophy_road_1v1_fights"),
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
    [
        sg.Text("Account Switches"),
    ],
]

bot_stats_values = [
    [
        stat_box("restarts_after_failure"),
    ],
    [
        stat_box("time_since_start", size=(7, 1)),
    ],
    [
        stat_box("account_switches", size=(7, 1)),
    ],
]

bot_stats = [
    [
        sg.Column(bot_stats_titles, element_justification="right"),
        sg.Column(bot_stats_values, element_justification="left"),
    ],
]
