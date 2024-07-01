import random

WINDOW_SIZE = (800, 600)

import PySimpleGUI as sg
from pyclashbot.interface.stats import (
    battle_stats,
    bot_stats,
    collection_stats,
)

# config keys
fightOption2key = {
    # fight stuff
    "Trophy road 1v1 battles": "trophy_road_toggle",
    "Goblin Queen's Journey battles": "goblin_queen_toggle",
    "Path of Legends 1v1 battles": "path_of_legends_toggle",
    "2v2 battles": "2v2_toggle",
    "War battles": "war_toggle",
    "Random decks": "random_decks_toggle",
    "Random plays": "random_plays_toggle",
    "Disable win/loss tracking": "disable_win_loss_tracking_toggle",
    "Skip fight when full chests": "skip_when_full_chests_toggle",
}
rewardsOption2key = {
    "Open chests": "open_chests_toggle",
    "Battlepass rewards": "battlepass_toggle",
    "Card mastery rewards": "card_mastery_toggle",
    "Daily Challenge Rewards": "daily_challenge_rewards_toggle",
    "Level Up Rewards": "level_up_chest_toggle",
    "Open Bannerbox Chests": "bannerbox_toggle",
    "Trophy Road Rewards": "trophy_road_rewards_toggle",
}
collectionOption2key = {
    "Request cards": "request_toggle",
    "Donate cards": "donate_toggle",
    "Buy FREE shop offers": "free_shop_offers_toggle",
    "Buy shop offers for GOLD": "gold_shop_offers_toggle",
    "Upgrade Cards": "upgrade_cards_toggle",
    "Upgrade ALL Cards": "upgrade_all_cards_toggle",
    "Season Shop Offers": "season_shop_toggle",
}
increment2key = {
    "Request Random Card Every:": "request_card_increment",
    "Donate Cards Every:": "donate_increment",
    "Collect Free Offer Every:": "free_shop_offer_increment",
    "Upgrade Current Deck Every:": "upgrade_deck_increment",
    "Collect Daily Rewards Every:": "daily_rewards_increment",
    "Collect Card Mastery Every:": "card_mastery_increment",
    "Open Chests Every:": "open_chests_increment",
    "Randomize Deck Every:": "randomize_deck_increment",
    "Do War Attack Every:": "war_increment",
    "Collect Battlepass Every:": "battlepass_increment",
    "Collect Level Up Chest Every:": "level_up_chest_increment",
    "Collect Trophy Road Rewards Every:": "trophy_road_rewards_increment",
    "Collect Season Shop Rewards Every:": "season_shop_rewards_increment",
    "Switch Account Every:": "switch_account_increment",
}

# compile config into a togglable list of keys
user_config_keys = []
for key_index in [1, 2]:
    for fight_option, key in fightOption2key.items():
        user_config_keys.append(f"{key}_{key_index}")

    for rewards_option, key in rewardsOption2key.items():
        user_config_keys.append(f"{key}_{key_index}")

    for collection_option, key in collectionOption2key.items():
        user_config_keys.append(f"{key}_{key_index}")

    for increment_text, key in increment2key.items():
        user_config_keys.append(f"{key}_{key_index}")

    user_config_keys.append(f"bot_toggle_{key_index}")


# buttons layout
def make_buttons_layout():
    button2colorKey = {
        "Start": ("GREEN", "start_key"),
        "Stop": ("RED", "Stop"),
        # "Collapse": ("GREEN", "-Collapse-Button-"),
        "Bug Report": ("grey", "bug-report"),
        "Upload Log": ("dark grey", "upload-log"),
        "Donate": ("GREEN", "donate"),
        "Discord": ("Purple", "discord"),
        "Exit": ("RED", "Exit"),
    }
    buttons_group = []
    for button, colorkey in button2colorKey.items():
        color, key = colorkey
        button = sg.Button(button, key=key, button_color=color)
        buttons_group.append(button)
    general_settings_layout = [[buttons_group]]
    return general_settings_layout


# bot controls page
def make_controls_layout(key_index):
    def make_bot_toggle_frame(key_index):
        default = True
        if str(key_index) == "2":
            default = False
        layout = [
            [
                sg.Checkbox(
                    "Enable Bot", default=default, key=f"bot_toggle_{key_index}"
                ),
            ]
        ]
        return sg.Frame(layout=layout, title="Bot Toggle", expand_x=True, expand_y=True)

    def make_job_increment_frame(key_index, increment2key):
        lt = []
        for increment_text, key in increment2key.items():
            key = key + f"_{key_index}"
            item = [
                sg.Text(increment_text, size=(30, 1)),
                sg.Input("1", size=(5, 1), key=key, background_color="grey"),
            ]
            lt.append(item)
        frame = sg.Frame(
            title="Job Increments", layout=lt, expand_x=True, expand_y=True
        )

        return frame

    def make_job_tabs_frame(
        key_index, fightOption2key, rewardsOption2key, collectionOption2key
    ):
        tab_layout = []

        # make fight options tab
        fight_options_layout = []
        for fight_option, key in fightOption2key.items():
            key = key + f"_{key_index}"
            fight_options_layout.append(
                [
                    sg.Checkbox(fight_option, key=key),
                ]
            )
        fight_options_tab = [sg.Tab("Fights", fight_options_layout)]
        tab_layout.append(fight_options_tab)

        # make rewards options tab
        rewards_options_layout = []
        for rewards_option, key in rewardsOption2key.items():
            key = key + f"_{key_index}"
            rewards_options_layout.append(
                [
                    sg.Checkbox(rewards_option, key=key),
                ]
            )
        rewards_options_tab = [sg.Tab("Rewards", rewards_options_layout)]
        tab_layout.append(rewards_options_tab)

        # make collection options tab
        collection_options_layout = []
        for collection_option, key in collectionOption2key.items():
            key = key + f"_{key_index}"
            collection_options_layout.append(
                [
                    sg.Checkbox(collection_option, key=key),
                ]
            )
        collection_options_tab = [sg.Tab("Collections", collection_options_layout)]
        tab_layout.append(collection_options_tab)

        tab = sg.TabGroup(tab_layout, expand_x=True, expand_y=True)

        frame = sg.Frame("Job Options", layout=[[tab]], expand_x=True, expand_y=True)

        return frame

    return [
        make_bot_toggle_frame(key_index),
        make_job_increment_frame(key_index, increment2key),
        make_job_tabs_frame(
            key_index, fightOption2key, rewardsOption2key, collectionOption2key
        ),
    ]


# stats page
def make_stats_layout():
    stats_tab_layout = [
        [
            sg.Column(
                [
                    [
                        sg.Frame(
                            layout=battle_stats,
                            title="Battle Stats",
                            expand_x=True,
                            expand_y=True,
                        )
                    ],
                    [
                        sg.Frame(
                            layout=bot_stats,
                            title="Bot Stats",
                            expand_x=True,
                        ),
                    ],
                ],
                expand_x=True,
                expand_y=True,
            ),
            sg.Column(
                [
                    [
                        sg.Frame(
                            layout=collection_stats,
                            title="Collection Stats",
                            expand_x=True,
                            expand_y=True,
                        ),
                    ],
                ],
                expand_x=True,
                justification="right",
                expand_y=True,
            ),
        ]
    ]
    return stats_tab_layout


# time and bot status bar
def make_time_status_bar_layout():
    time_status_bar_layout = [
        sg.Frame(
            title="Bot #1",
            layout=[
                [
                    sg.Column(
                        [
                            # account switching stuff
                            [
                                sg.Text("Bot #1 Accounts:"),
                                sg.Slider(
                                    range=(1, 8),
                                    orientation="horizontal",
                                    key="accounts_slider_1",
                                ),
                            ],
                            [
                                sg.Input(
                                    "Idle",
                                    key="current_status_1",
                                    use_readonly_for_disable=True,
                                    disabled=True,
                                    text_color="blue",
                                    expand_x=True,
                                ),
                            ],
                            [
                                sg.Text(
                                    "VM Index: ",
                                    text_color="blue",
                                ),
                                sg.Text(
                                    "-1",
                                    key="bot_1_vm_index",
                                    text_color="blue",
                                    expand_x=True,
                                ),
                            ],
                            [
                                sg.Text(
                                    "Account order:",
                                    text_color="blue",
                                    expand_x=True,
                                ),
                                sg.Text(
                                    "[]",
                                    key="account_order_1",
                                    text_color="blue",
                                    expand_x=True,
                                ),
                            ],
                        ],
                        expand_x=True,
                    ),
                ]
            ],
        ),
        sg.Frame(
            title="Bot #2",
            layout=[
                [
                    sg.Column(
                        [
                            [
                                sg.Text("Bot #2 Accounts:"),
                                sg.Slider(
                                    range=(1, 8),
                                    orientation="horizontal",
                                    key="accounts_slider_2",
                                ),
                            ],
                            [
                                sg.Input(
                                    "Idle",
                                    key="current_status_2",
                                    use_readonly_for_disable=True,
                                    disabled=True,
                                    text_color="blue",
                                    expand_x=True,
                                ),
                            ],
                            [
                                sg.Text(
                                    "VM Index: ",
                                    text_color="blue",
                                ),
                                sg.Text(
                                    "-1",
                                    key="bot_2_vm_index",
                                    text_color="blue",
                                    expand_x=True,
                                ),
                            ],
                            [
                                sg.Text(
                                    "Account order:",
                                    text_color="blue",
                                    expand_x=True,
                                ),
                                sg.Text(
                                    "[]",
                                    key="account_order_2",
                                    text_color="blue",
                                    expand_x=True,
                                ),
                            ],
                        ],
                        expand_x=True,
                    ),
                ]
            ],
        ),
    ]
    return time_status_bar_layout


def make_donate_layout():
    image_layout = [
        sg.Image(r"src\pyclashbot\interface\assets\donate1.png"),
    ]

    return image_layout


def make_window():
    # Define the layout for each tab
    bot1_tab = [make_controls_layout(1)]
    bot2_tab = [make_controls_layout(2)]
    stats_tab = make_stats_layout()

    # Define the layout for the main tab group
    layout = [
        [
            sg.TabGroup(
                [
                    [
                        sg.Tab(
                            "Bot #1 Settings", bot1_tab, expand_x=True, expand_y=True
                        ),
                        sg.Tab(
                            "Bot #2 Settings", bot2_tab, expand_x=True, expand_y=True
                        ),
                        sg.Tab("Stats", stats_tab, expand_x=True, expand_y=True),
                    ]
                ],
                expand_x=True,
                expand_y=True,
            ),
        ],
        [
            make_buttons_layout(),
            make_time_status_bar_layout(),
            make_donate_layout(),
        ],
    ]

    # Create the window
    window = sg.Window(
        "Py-ClashBot",
        layout,
        finalize=True,
    )

    return window


def make_job_dict(values):
    def is_trash_key(key):
        # if its just an int, its trash
        try:
            int(key)
            return True
        except:
            pass

        # if its 3 or less in len
        if len(key) <= 3:
            return True

        return False

    def format_key(key):
        key = key.replace("_1", "").replace("_2", "")
        return key

    def make_account_order_list(count):
        list = []
        while len(list) < count:
            r = random.randint(0, count - 1)
            if r not in list:
                list.append(r)

        return list

    botIndex2jobList = {
        1: {},
        2: {},
    }

    for key, value in values.items():
        key = str(key)
        if is_trash_key(key):
            continue
        write_key = format_key(key)
        # replace any ints with nothing
        if "_1" in key:
            if "accounts_slider" in key:
                botIndex2jobList[1]["account_order_1"] = make_account_order_list(
                    int(value)
                )
            botIndex2jobList[1][write_key] = value
        elif "_2" in key:
            if "accounts_slider" in key:
                botIndex2jobList[2]["account_order_2"] = make_account_order_list(
                    int(value)
                )
            botIndex2jobList[2][write_key] = value
        else:
            if "accounts_slider" in key:
                botIndex2jobList[1]["account_order_1"] = make_account_order_list(
                    int(value)
                )
                botIndex2jobList[2]["account_order_2"] = make_account_order_list(
                    int(value)
                )
            botIndex2jobList[1][write_key] = value
            botIndex2jobList[2][write_key] = value

    return botIndex2jobList


if __name__ == "__main__":
    window = make_window()

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break

        if event == "start_key":
            botIndex2jobList = make_job_dict(values)

            for bot_index, job_list in botIndex2jobList.items():
                print("bot_index:", bot_index)
                for key, value in job_list.items():
                    print("\t", key, value)

    window.close()
