"""a dummy test function to simulate the interface"""

import time
import webbrowser
from typing import Any

import PySimpleGUI as sg

from pyclashbot.interface.help import show_help_gui
from pyclashbot.interface.layout import disable_keys, main_layout
from pyclashbot.interface.theme import THEME

sg.theme(THEME)

if __name__ == "__main__":

    # some sample statistics
    statistics: dict[str, Any] = {
        "wins": 1,
        "losses": 2,
        "fights": 3,
        "requests": 4,
        "restarts": 5,
        "chests_unlocked": 6,
        "cards_played": 7,
        "cards_upgraded": 8,
        "account_switches": 9,
        "card_mastery_reward_collections": 10,
        "battlepass_rewards_collections": 11,
        "level_up_chest_collections": 12,
        "war_battles_fought": 13,
        "current_status": "Starting",
    }

    window = sg.Window("Py-ClashBot", main_layout)

    running = False  # pylint: disable=invalid-name

    while True:
        event, values = window.read(timeout=100)  # type: ignore
        if event == sg.WIN_CLOSED:
            break
        if event == "Start":
            window["current_status"].update("Starting")  # type: ignore
            for key in disable_keys:
                window[key].update(disabled=True)
            running = True  # pylint: disable=invalid-name
            window["Stop"].update(disabled=False)

        elif event == "Stop":
            window["current_status"].update("Stopping")  # type: ignore
            running = False  # pylint: disable=invalid-name
            for key in disable_keys:
                window[key].update(disabled=False)
            window["Stop"].update(disabled=True)

        elif event == "Help":
            show_help_gui()

        elif event == "Donate":
            webbrowser.open(
                "https://www.paypal.com/donate/"
                + "?business=YE72ZEB3KWGVY"
                + "&no_recurring=0"
                + "&item_name=Support+my+projects%21"
                + "&currency_code=USD"
            )

        elif event == "issues-link":
            webbrowser.open(
                "https://github.com/matthewmiglio/py-clash-bot/issues/new/choose"
            )

        if running:
            # change some of the statistics
            statistics["wins"] += 1
            statistics["losses"] += 1
            statistics["fights"] += 1
            statistics["war_battles_fought"] += 1
            statistics["requests"] += 1

        # update the statistics
        window["wins"].update(statistics["wins"])
        window["losses"].update(statistics["losses"])
        window["fights"].update(statistics["fights"])
        window["war_battles_fought"].update(statistics["war_battles_fought"])
        window["requests"].update(statistics["requests"])

        time.sleep(1)

    window.close()
