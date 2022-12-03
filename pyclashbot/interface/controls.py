import PySimpleGUI as sg

from pyclashbot.interface.theme import THEME

sg.theme(THEME)

controls = [
    [
        sg.Column(
            [
                [
                    sg.Button("Start"),
                    sg.Button("Stop", disabled=True),
                    sg.Button("Pause", disabled=True, key="-Pause-Resume-Button-"),
                ],
                [
                    sg.Text("# of Accounts: "),
                    sg.Combo(
                        ["1", "2", "3", "4", "5", "6", "7", "8"],
                        key="-SSID_IN-",
                        default_value="1",
                        enable_events=True,
                    ),
                ],
                [
                    sg.Button("Help"),
                    sg.Button("Donate"),
                ],
            ],
        ),
    ],
]
