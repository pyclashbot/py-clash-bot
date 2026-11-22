"""Battle configuration errors shared by fight/nav/state modules.

Kept in a leaf module so ``nav``, ``fight`` and ``states`` can all raise or catch
this without importing each other.
"""

from __future__ import annotations


class BattleDeckIncompleteError(RuntimeError):
    """The game refused the match because the Battle Deck has fewer than 8 cards."""
