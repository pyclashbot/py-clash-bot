import PySimpleGUI as sg
from pyclashbot.interface.stats import (
    stat_box,
)
from pyclashbot.interface.theme import THEME

sg.theme(THEME)
layout1 = [
    [sg.Text("Name", size=(10, 1)), sg.Input("", key="eName")],
    [sg.Text("Date of Birth", size=(10, 1)), sg.Input("", key="eDob")],
    [sg.Text("Phone No", size=(10, 1)), sg.Input("", key="ePhone")],
    [sg.Text("Email ID", size=(10, 1)), sg.Input("", key="eEmail")],
    [sg.Button("Save Personal Details")],
]
layout2 = [
    [sg.Text("Highest Qualfication", size=(15, 1)), sg.Input("", key="eQual")],
    [sg.Text("Year of Qualifying", size=(15, 1)), sg.Input("", key="eYoq")],
    [sg.Text("Grade", size=(15, 1)), sg.Input("", key="eGrade")],
    [sg.Text("University/College", size=(15, 1)), sg.Input("", key="eQUniv")],
    [sg.Button("Save Education Details")],
]
layout3 = [
    [sg.Text("Last Job", size=(10, 1)), sg.Input("", key="eLastJ")],
    [sg.Text("From Date", size=(10, 1)), sg.Input("", key="eJFdt")],
    [sg.Text("To Date", size=(10, 1)), sg.Input("", key="eJTdt")],
    [sg.Text("Company Name", size=(10, 1)), sg.Input("", key="eLJcmpy")],
    [sg.Button("Save Experience Details")],
]

test_stats_titles = [
    [
        sg.Text("Wins: "),
    ],
    [
        sg.Text("Losses: "),
    ],
    [
        sg.Text("Cards Played: "),
    ],
    [
        sg.Text("2v2 Fights: "),
    ],
    [
        sg.Text("War Battles Fought: "),
    ],
]

test_stats_values = [
    [
        stat_box("wins"),
    ],
    [
        stat_box("losses"),
    ],
    [
        stat_box("cards_played"),
    ],
    [
        stat_box("fights"),
    ],
    [
        stat_box("war_battles_fought"),
    ],
]

test_stats = [
    [
        sg.Column(test_stats_titles, element_justification="right"),
        sg.Column(test_stats_values, element_justification="left"),
    ]
]

# Define Layout with Tabs
main_layout = [
    [
        sg.TabGroup(
            [
                [
                    sg.Tab(
                        "Personal Details",
                        layout1,
                        # title_color="Red",
                        border_width=10,
                        # background_color="Green",
                        tooltip="Personal details",
                        element_justification="center",
                    ),
                    sg.Tab(
                        "Education",
                        layout2,
                        # title_color="Blue",
                        # background_color="Yellow",
                    ),
                    sg.Tab(
                        "Experience",
                        layout3,
                        # title_color="Black",
                        # background_color="Pink",
                        tooltip="Enter  your Lsst job experience",
                    ),
                ]
            ],
            tab_location="topleft",
            # title_color="Red",
            # tab_background_color="Purple",
            # selected_title_color="Green",
            # selected_background_color="Gray",
            border_width=5,
        ),
    ],
    [
        sg.Frame(
            layout=test_stats,
            title="Battle Stats",
        ),
    ],
    [
        sg.Text("Output", expand_x=True, justification="center"),
        sg.Button("Close"),
    ],
]

window = sg.Window("Tabs", main_layout)
# Read  values entered by user
event, values = window.read()
# access all the values and if selected add them to a string
window.close()
