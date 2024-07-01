"""pysimplegui layout for the joblist window."""

import PySimpleGUI as sg

from pyclashbot.interface.theme import THEME

sg.theme(THEME)


def no_jobs_popup() -> None:
    """pysimplegui to popup when no jobs are selected."""

    # Define the layout of the GUI
    layout = [
        [
            sg.Text(
                "You must select at least one job!",
                size=(25, 2),
                justification="center",
            )
        ],
        [sg.Button("Exit", size=(10, 1), pad=((150, 0), 3))],
    ]

    # Create the window
    window = sg.Window("Critical Error!", layout)

    # Event loop to process events and get user input
    while True:
        event, *_ = window.read()  # type: ignore

        # Exit the program if the "Exit" button is clicked or window is closed
        if event in (sg.WINDOW_CLOSED, "Exit"):
            break

    # Close the window
    window.close()


def job_check_box(text: str, element_key: str, default_value=True) -> sg.Checkbox:
    """returns a checkbox element for the joblist window"""

    return sg.Checkbox(
        text,
        default=default_value,
        key=element_key,
        enable_events=True,
    )


def make_battle_tab(index):

    battle_tab = (
        [
            job_check_box(
                "Trophy road 1v1 battles",
                f"trophy_road_1v1_user_toggle_{index}",
                default_value=False,
            ),
        ],
        [
            job_check_box(
                "Goblin Queen's Journey battles",
                f"goblin_queens_journey_1v1_battle_user_toggle_{index}",
                default_value=False,
            ),
        ],
        [
            job_check_box(
                "Path of Legends 1v1 battles",
                f"path_of_legends_1v1_user_toggle_{index}",
                default_value=False,
            ),
        ],
        [
            job_check_box("2v2 battles", f"2v2_user_toggle_{index}", default_value=True),
        ],
        [
            job_check_box("War battles", f"war_user_toggle_{index}", default_value=False),
        ],
        [
            job_check_box(
                "Random decks", f"random_decks_user_toggle_{index}", default_value=False
            ),
        ],
        [
            job_check_box(
                "Random plays", f"random_plays_user_toggle_{index}", default_value=False
            ),
        ],
        [
            job_check_box(
                "Disable win/loss tracking",
                f"disable_win_track_toggle_{index}",
                default_value=False,
            ),
        ],
        [
            job_check_box(
                "Skip fight when full chests",
                f"skip_fight_if_full_chests_user_toggle_{index}",
                default_value=False,
            ),
        ],
    )

    return battle_tab


def make_rewards_tab(index):
    rewards_tab = [
        [
            job_check_box("Open chests", f"open_chests_user_toggle_{index}", default_value=True),
        ],
        [
            job_check_box(
                "Battlepass rewards", f"open_battlepass_user_toggle_{index}", default_value=False
            ),
        ],
        [
            job_check_box(
                "Card mastery rewards", f"card_mastery_user_toggle_{index}", default_value=False
            ),
        ],
        [
            job_check_box(
                "Daily Challenge Rewards",
                f"daily_rewards_user_toggle_{index}",
                default_value=False,
            ),
        ],
        [
            job_check_box(
                "Level Up Rewards", f"level_up_chest_user_toggle_{index}", default_value=False
            ),
        ],
        [
            job_check_box(
                "Open Bannerbox Chests",
                f"open_bannerbox_user_toggle_{index}",
                default_value=False,
            ),
        ],
        [
            job_check_box(
                "Trophy Road Rewards",
                f"trophy_road_rewards_user_toggle_{index}",
                default_value=False,
            ),
        ],
    ]

    return rewards_tab


def make_card_collection_tab(index):
    card_collection_tab = [
        [
            job_check_box("Request cards", f"request_user_toggle_{index}", default_value=False),
        ],
        [
            job_check_box("Donate cards", f"donate_toggle_{index}", default_value=False),
        ],
        [
            job_check_box(
                "Buy FREE shop offers", f"free_offer_user_toggle_{index}", default_value=True
            ),
        ],
        [
            job_check_box(
                "Buy shop offers for GOLD",
                f"gold_offer_user_toggle_{index}",
                default_value=False,
            ),
        ],
        [
            job_check_box(
                "Upgrade Cards", f"card_upgrade_user_toggle_{index}", default_value=False
            ),
        ],
        [
            job_check_box(
                "Upgrade ALL Cards",
                f"upgrade_all_cards_user_toggle_{index}",
                default_value=False,
            ),
        ],
        [
            job_check_box(
                "Season Shop Offers",
                f"season_shop_buys_user_toggle_{index}",
                default_value=False,
            ),
        ],
    ]

    return card_collection_tab


def make_jobs_checklist(index):
    jobs_checklist = [
        [
            # layout:List[List[Tab]]
            sg.TabGroup(
                layout=[
                    [sg.Tab("Battle Jobs", make_battle_tab(index))],
                    [sg.Tab("Collection Jobs", make_rewards_tab(index))],
                    [sg.Tab("Cards Jobs", make_card_collection_tab(index))],
                ]
            )
        ]
    ]
    return jobs_checklist
