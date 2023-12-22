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


jobs_checklist = [
    [
        sg.Column(
            [
                [
                    job_check_box(
                        "1v1 battles", "1v1_user_toggle", default_value=False
                    ),
                ],
                [
                    job_check_box("2v2 battles", "2v2_user_toggle"),
                ],
                [
                    job_check_box("Open chests", "open_chests_user_toggle"),
                ],
                [
                    job_check_box("Random Requesting", "request_user_toggle"),
                ],
                [
                    job_check_box("Donates", "donate_toggle"),
                ],
                [
                    job_check_box(
                        "Card Mastery Collection", "card_mastery_user_toggle"
                    ),
                ],
                [
                    job_check_box(
                        "Free Offers Collection",
                        "free_offer_user_toggle",
                    ),
                ],
                [
                    job_check_box(
                        "Gold Offers Collection",
                        "gold_offer_user_toggle",
                    ),
                ],
                [
                    job_check_box(
                        "Disable win/loss tracking",
                        "disable_win_track_toggle",
                    ),
                ],
                [
                    job_check_box(
                        "War Participation",
                        "war_user_toggle",
                    ),
                ],
                [
                    job_check_box(
                        "Open Bannerbox",
                        "open_bannerbox_user_toggle",
                    ),
                ],
                [
                    job_check_box(
                        "Daily Rewards",
                        "daily_rewards_user_toggle",
                    ),
                ],
                [
                    job_check_box(
                        "Card Upgrading",
                        "card_upgrade_user_toggle",
                        default_value=False,
                    ),
                ],
                [
                    job_check_box(
                        "Random Decks", "random_decks_user_toggle", default_value=False
                    ),
                ],
                [
                    job_check_box(
                        "Random Plays", "random_plays_user_toggle", default_value=False
                    ),
                ],
                [
                    job_check_box(
                        "Skip Fights When Full Chests",
                        "skip_fight_if_full_chests_user_toggle",
                        default_value=False,
                    ),
                ],
            ],
            scrollable=True,
            vertical_scroll_only=True,
            expand_x=True,
            size=(None, 285),
        )
    ],
]
