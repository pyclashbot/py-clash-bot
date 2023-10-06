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


controls = [
    [
        sg.Button("Start", expand_x=True,button_color='Lime Green'),
        sg.Button("Stop", disabled=True, expand_x=True),
        sg.Button("Pause", disabled=True, key="-Pause-Resume-Button-", expand_x=True),
    ],
    # whole box
    [
        # title column
        sg.Column(
            [
                [sg.Text("Request Random Card Every:")],
                [sg.Text("Collect Free Offer Every:")],
                [sg.Text("Upgrade Current Deck Every:")],
                [sg.Text("Collect Card Mastery Every:")],
                [sg.Text("Open Chests Every:")],
                [sg.Text("Randomize Deck Every:")],
                [sg.Text("Do war attack Every:")],
            ],
            justification="left",
        ),
        # input text column
        sg.Column(
            [
                [make_job_increment_control_object("request_increment_user_input")],
                [
                    make_job_increment_control_object(
                        "free_offer_collection_increment_user_input"
                    )
                ],
                [
                    make_job_increment_control_object(
                        "card_upgrade_increment_user_input"
                    )
                ],
                [
                    make_job_increment_control_object(
                        "card_mastery_collect_increment_user_input"
                    )
                ],
                [make_job_increment_control_object("open_chests_increment_user_input")],
                [
                    make_job_increment_control_object(
                        "deck_randomization_increment_user_input"
                    )
                ],
                [make_job_increment_control_object("war_attack_increment_user_input")],

            ],
            justification="right",
        ),
        # end titles column
        sg.Column(
            [
                [sg.Text("games")],
                [sg.Text("games")],
                [sg.Text("games")],
                [sg.Text("games")],
                [sg.Text("games")],
                [sg.Text("games")],
            ],
            justification="left",
        ),
    ],
    [sg.VP()],
    [sg.HSep(color="lightgray")],
    [
        sg.Button("Discord", key="discord", expand_x=True, button_color="#7289da"),
        sg.Button("Upload Log", key="upload-log", expand_x=True),
        sg.Button("Report Bug", key="bug-report", expand_x=True),
    ],
]
