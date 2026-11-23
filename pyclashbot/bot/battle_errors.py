"""Battle configuration errors shared by fight/nav/state modules.

Kept in a leaf module so ``nav``, ``fight`` and ``states`` can all raise or catch
this without importing each other.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, NoReturn

if TYPE_CHECKING:
    from pyclashbot.utils.logger import Logger


class BattleDeckIncompleteError(RuntimeError):
    """The game refused the match because the Battle Deck has fewer than 8 cards."""


def raise_deck_incomplete(logger: Logger) -> NoReturn:
    logger.change_status("Battle Deck incomplete — fill 8/8")
    logger.log("The game refused the match: the Battle Deck needs 8 cards.")
    raise BattleDeckIncompleteError("Battle Deck incomplete — fill 8/8")


def raise_empty_deck(logger: Logger) -> NoReturn:
    logger.change_status("Battle Deck incomplete — fill 8/8")
    logger.log("The Battle Deck has no cards.")
    raise BattleDeckIncompleteError("Battle Deck incomplete — fill 8/8")
