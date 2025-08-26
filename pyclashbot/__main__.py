"""This module contains the main entry point for the Royale Engine program.
It provides a customtkinter GUI interface for users to configure and run the bot.
"""

from pyclashbot.gui_tk import BotGUI
from pyclashbot.utils.cli_config import arg_parser
from pyclashbot.utils.logger import initalize_pylogging

initalize_pylogging()


def main_gui_tk() -> None:
    """Main entry point for the customtkinter GUI application."""
    app = BotGUI()
    app.run()


if __name__ == "__main__":
    cli_args = arg_parser()
    main_gui_tk()