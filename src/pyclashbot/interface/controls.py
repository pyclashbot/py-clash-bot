"""pysimplegui layout for the controls tab"""
import PySimpleGUI as sg

from pyclashbot.interface.theme import THEME

sg.theme(THEME)


controls = [
    [
        sg.Button("Start", expand_x=True),
        sg.Button("Stop", disabled=True, expand_x=True),
        sg.Button("Pause", disabled=True, key="-Pause-Resume-Button-", expand_x=True),
    ],
    [
        sg.Column(
            [
                [sg.Text("Request Random Card Every:")],
                [sg.Text("Collect Free Offer Every:")],
                [sg.Text("Upgrade Current Deck Every:")],
                [sg.Text("Collect Card Mastery Every:")],
                [sg.Text("Open Chests Every:")],
                [sg.Text("Randomize Deck Every:")],
            ],
            justification="left",
        ),
        sg.Column(
            [
                [
                    sg.DropDown(
                        ["1 game", "3 games", "5 games", "10 games", "25 games"],
                        key="request_increment_user_input",
                        default_value="1 game",
                        enable_events=True,
                    )
                ],
                [
                    sg.DropDown(
                        ["1 game", "3 games", "5 games", "10 games", "25 games"],
                        key="free_offer_collection_increment_user_input",
                        default_value="1 game",
                        enable_events=True,
                    )
                ],
                [
                    sg.DropDown(
                        ["1 game", "3 games", "5 games", "10 games", "25 games"],
                        key="card_upgrade_increment_user_input",
                        default_value="1 game",
                        enable_events=True,
                    )
                ],
                [
                    sg.DropDown(
                        ["1 game", "3 games", "5 games", "10 games", "25 games"],
                        key="card_mastery_collect_increment_user_input",
                        default_value="1 game",
                        enable_events=True,
                    )
                ],
                [
                    sg.DropDown(
                        ["1 game", "3 games", "5 games", "10 games", "25 games"],
                        key="open_chests_increment_user_input",
                        default_value="1 game",
                        enable_events=True,
                    )
                ],
                [
                    sg.DropDown(
                        ["1 game", "3 games", "5 games", "10 games", "25 games"],
                        key="deck_randomization_increment_user_input",
                        default_value="1 game",
                        enable_events=True,
                    )
                ],
            ],
            justification="right",
        ),
    ],
    [sg.VP()],
    [sg.HSep(color="lightgray")],
    [
        sg.Button("Discord", key="discord", expand_x=True),
        sg.Button("Report Bug", key="bug-report", expand_x=True),
    ],
]
