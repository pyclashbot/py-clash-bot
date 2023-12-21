"""
This module provides a PyMemuc singleton instance.
"""

import sys
from os.path import join

from pymemuc import PyMemuc

FROZEN = getattr(sys, "frozen", False)

pmc = PyMemuc()

adb_path = join(
    # pylint: disable=protected-access
    pmc._get_memu_top_level(),
    "adb.exe",
)
