"""Module to parse arguments from CLI"""

from argparse import ArgumentParser, Namespace


def arg_parser() -> Namespace:
    """Function to parse arguments

    Returns
    -------
        Namespace: populated namespace from arguments

    """
    parser = ArgumentParser(description="Run py-clash-bot from CLI")
    parser.add_argument(
        "--start",
        "-s",
        dest="start",
        action="store_true",
        help="Start the bot when the program opens",
    )
    parser.add_argument(
        "--ui",
        "-u",
        dest="ui",
        type=str,
        choices=["web", "regular"],
        default=None,
        help="UI mode: 'web' for webview UI, 'regular' for tkinter UI (default: from settings)",
    )
    return parser.parse_args()
