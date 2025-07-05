"""FreeSimpleGUI layout for the joblist window."""

import FreeSimpleGUI as sg

from pyclashbot.interface.theme import THEME

sg.theme(THEME)


def no_jobs_popup() -> None:
    """FreeSimpleGUI to popup when no jobs are selected."""
    # Define the layout of the GUI
    layout = [
        [
            sg.Text(
                "You must select at least one job!",
                size=(25, 2),
                justification="center",
            ),
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
    """Returns a checkbox element for the joblist window"""
    return sg.Checkbox(
        text,
        default=default_value,
        key=element_key,
        enable_events=True,
    )


battle_tab = (
    [
        job_check_box(
            "Trophy road battles",
            "trophy_road_1v1_user_toggle",
            default_value=False,
        ),
    ],
    [
        job_check_box("War battles", "war_user_toggle", default_value=False),
    ],
    [
        job_check_box("Random decks", "random_decks_user_toggle", default_value=False),
        sg.Text("Deck #:", size=(5, 1)),
        sg.Combo(
            values=[1, 2, 3, 4, 5],
            default_value=2,
            key="deck_number_selection",
            size=(5, 1),
            readonly=True,
            enable_events=True
        ),
    ],
    [
        job_check_box("Random plays", "random_plays_user_toggle", default_value=False),
    ],
    [
        job_check_box(
            "Skip win/loss check",
            "disable_win_track_toggle",
            default_value=False,
        ),
    ],
)


rewards_tab = [
    [
        job_check_box(
            "Battlepass",
            "open_battlepass_user_toggle",
            default_value=False,
        ),
    ],
    [
        job_check_box(
            "Card Masteries",
            "card_mastery_user_toggle",
            default_value=False,
        ),
    ],
    [
        job_check_box(
            "Level Up Rewards",
            "level_up_chest_user_toggle",
            default_value=False,
        ),
    ],
    [
        job_check_box(
            "Trophy Road Rewards",
            "trophy_road_rewards_user_toggle",
            default_value=False,
        ),
    ],
    [
        job_check_box(
            "Spend Magic Items",
            "magic_items_user_toggle",
            default_value=False,
        ),
    ],
]


card_collection_tab = [
    [
        job_check_box("Request cards", "request_user_toggle", default_value=False),
    ],
    [
        job_check_box("Donate cards", "donate_toggle", default_value=False),
    ],
    [
        job_check_box(
            "Donate cards for FREE ",
            "free_donate_toggle",
            default_value=False,
        ),
    ],
    [
        job_check_box(
            "Buy FREE shop offers",
            "free_offer_user_toggle",
            default_value=True,
        ),
    ],
    [
        job_check_box(
            "Buy shop offers",
            "gold_offer_user_toggle",
            default_value=False,
        ),
    ],
    [
        job_check_box("Upgrade Cards", "card_upgrade_user_toggle", default_value=False),
    ],
    [
        job_check_box(
            "Season Shop Offers",
            "season_shop_buys_user_toggle",
            default_value=False,
        ),
    ],
]


jobs_checklist = [
    [
        # layout:List[List[Tab]]
        sg.TabGroup(
            layout=[
                [sg.Tab("Battle", battle_tab)],
                [sg.Tab("Collection", rewards_tab)],
                [sg.Tab("Cards", card_collection_tab)],
            ],
            border_width=0,
            tab_border_width=0,
        ),
    ],
]
