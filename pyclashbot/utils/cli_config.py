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
        "--debug",
        "-d",
        dest="debug",
        action="store_true",
        help="Enable debug-level logging",
    )
    return parser.parse_args()
