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
        sg.Text("Request every:             "),
        sg.Column(
            [
                [
                    sg.DropDown(
                        ["1 game", "5 games", "25 games"],
                        key="request_increment_user_input",
                        default_value="1 game",
                    )
                ],
            ],
            justification="right",
            expand_x=True,
        ),
    ],
    [
        sg.Text("Collect free offer every:  "),
        sg.Column(
            [
                [
                    sg.DropDown(
                        ["1 game", "5 games", "25 games"],
                        key="free_offer_collection_increment_user_input",
                        default_value="1 game",
                    )
                ],
            ],
            justification="right",
            expand_x=True,
        ),
    ],
    [
        sg.Text("Upgrade cards every:    "),
        sg.Column(
            [
                [
                    sg.DropDown(
                        ["1 game", "5 games", "25 games"],
                        key="card_upgrade_increment_user_input",
                        default_value="1 game",
                    )
                ],
            ],
            justification="right",
            expand_x=True,
        ),
    ],
    [sg.VP()],
    [sg.HSep(color="lightgray")],
    [
        sg.Button("Discord", key="discord", expand_x=True),
        sg.Button("Report Bug", key="bug-report", expand_x=True),
    ],
]
