"""Module to parse arguments from CLI"""
from argparse import ArgumentParser, Namespace


def arg_parser() -> Namespace:
    """function to parse arguments

    Returns:
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
    return parser.parse_args()
