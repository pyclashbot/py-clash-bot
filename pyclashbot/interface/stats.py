"""FreeSimpleGUI layout for stats tab"""

import FreeSimpleGUI as sg  # noqa: N813

from pyclashbot.interface.theme import THEME

sg.theme(THEME)


def stat_box(stat_name: str, size=(5, 1)) -> sg.Text:
    """Returns a FreeSimpleGUI text box object for stats layout"""
    return sg.Text(
        "0", key=stat_name, relief=sg.RELIEF_SUNKEN, text_color="blue", size=size, pad=0
    )


def make_stat_titles(titles: list[str]) -> list[list[sg.Text]]:
    list = [[sg.Text(title, pad=0)] for title in titles]
    return list


# collection stats
collection_title_texts = [
    "Card Masteries",
    "Cards Upgraded",
    "War Chests",
]


collection_stats_titles: list[list[sg.Text]] = make_stat_titles(collection_title_texts)

collection_stats_values: list[list[sg.Text]] = [
    [
        stat_box("card_mastery_reward_collections"),
    ],
    [
        stat_box("upgrades"),
    ],
    [
        stat_box("war_chest_collects"),
    ],
]

collection_stats = [
    [
        sg.Column(collection_stats_titles, element_justification="right"),
        sg.Column(collection_stats_values, element_justification="left"),
    ],
]


# fight stats
titles = [
    "Wins",
    "Losses",
    "Win Rate",
    "Cards Played",
    "Trophy Battles",
    "Random Decks",
]

battle_stats_titles: list[list[sg.Text]] = make_stat_titles(titles)


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
        stat_box("trophy_road_1v1_fights"),
    ],
    [
        stat_box("card_randomizations"),
    ],
]

battle_stats = [
    [
        sg.Column(battle_stats_titles, element_justification="right", pad=0),
        sg.Column(battle_stats_values, element_justification="left", pad=0),
    ],
]


# bot stats

bot_stat_title_texts = [
    "Bot Failures",
    "Runtime",
]

bot_stats_titles: list[list[sg.Text]] = make_stat_titles(bot_stat_title_texts)

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
