import PySimpleGUI as sg

from interface.theme import THEME

sg.theme(THEME)


def job_check_box(text: str, element_key: str) -> sg.Checkbox:
    return sg.Checkbox(
        text,
        default=True,
        key=element_key,
        enable_events=True,
    )


jobs_checklist = [
    [
        sg.Column(
            [
                [
                    job_check_box("Open chests", "-Open-Chests-in-"),
                ],
                [
                    job_check_box("1v1 battles", "1v1_battle_in"),
                ],
                [
                    job_check_box("Random Requesting", "-Requesting-in-"),
                ],
                [
                    job_check_box(
                        "Card Mastery Collection", "-Card-Mastery-Collection-in-"
                    ),
                ],
                [
                    job_check_box(
                        "Free Offer Collection",
                        "-Free-Offer-Collection-in-",
                    ),
                ],
            ],
            scrollable=True,
            vertical_scroll_only=True,
            expand_x=True,
            size=(None, 150),
        )
    ],
]
