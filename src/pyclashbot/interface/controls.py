"""pysimplegui layout for the controls tab"""

import PySimpleGUI as sg

from pyclashbot.interface.theme import THEME

sg.theme(THEME)


def make_job_increment_control_object(key):
    return sg.InputText(
        default_text="1",
        tooltip="How often to perform this job",
        key=key,
        enable_events=True,
        size=5,
    )


job_increments_titles_column = [
    [sg.Text("Request Random Card Every:")],
    [sg.Text("Donate Cards Every:")],
    [sg.Text("Collect Shop Offers Every:")],
    [sg.Text("Upgrade Current Deck Every:")],
    [sg.Text("Collect Daily Rewards Every:")],
    [sg.Text("Collect Card Mastery Every:")],
    [sg.Text("Open Chests Every:")],
    [sg.Text("Randomize Deck Every:")],
    [sg.Text("Do War Attack Every:")],
    [sg.Text("Collect Battlepass Every:")],
    [sg.Text("Collect Level Up Chest Every:")],
    [sg.Text("Collect Trophy Road Rewards Every:")],
    [sg.Text("Collect Season Shop Rewards Every:")],
    [sg.Text("Switch Account Every:")],
]

games_titles_column = []
for _ in range(len(job_increments_titles_column)):
    games_titles_column.append([sg.Text("games")])


def make_controls_tab(index):
    controls = [
        # whole box
        [
            # title column
            sg.Column(
                job_increments_titles_column,
                justification="left",
            ),
            # input text column
            sg.Column(
                [
                    [
                        make_job_increment_control_object(
                            f"request_increment_user_input_{index}"
                        )
                    ],
                    [
                        make_job_increment_control_object(
                            f"donate_increment_user_input_{index}"
                        )
                    ],
                    [
                        make_job_increment_control_object(
                            f"shop_buy_increment_user_input_{index}"
                        )
                    ],
                    [
                        make_job_increment_control_object(
                            f"card_upgrade_increment_user_input_{index}"
                        )
                    ],
                    [
                        make_job_increment_control_object(
                            f"daily_reward_increment_user_input_{index}"
                        )
                    ],
                    [
                        make_job_increment_control_object(
                            f"card_mastery_collect_increment_user_input_{index}"
                        )
                    ],
                    [
                        make_job_increment_control_object(
                            f"open_chests_increment_user_input_{index}"
                        )
                    ],
                    [
                        make_job_increment_control_object(
                            f"deck_randomization_increment_user_input_{index}"
                        )
                    ],
                    [
                        make_job_increment_control_object(
                            f"war_attack_increment_user_input_{index}"
                        )
                    ],
                    [
                        make_job_increment_control_object(
                            f"battlepass_collect_increment_user_input_{index}"
                        )
                    ],
                    [
                        make_job_increment_control_object(
                            f"level_up_chest_increment_user_input_{index}"
                        )
                    ],
                    [
                        make_job_increment_control_object(
                            f"trophy_road_reward_increment_user_input_{index}"
                        )
                    ],
                    [
                        make_job_increment_control_object(
                            f"season_shop_buys_increment_user_input_{index}"
                        )
                    ],
                    [
                        make_job_increment_control_object(
                            f"account_switching_increment_user_input_{index}"
                        )
                    ],
                ],
                justification="right",
            ),
            # end titles column
            sg.Column(
                games_titles_column,
                justification="left",
            ),
        ],
        [sg.VP()],
        [sg.HSep(color="lightgray")],
    ]

    return controls
