"""
This module provides a PyMemuc singleton instance.
"""

import sys

from pymemuc import PyMemuc

FROZEN = getattr(sys, "frozen", False)

# pmc = PyMemuc(debug=not FROZEN)
pmc = PyMemuc(debug=False)
