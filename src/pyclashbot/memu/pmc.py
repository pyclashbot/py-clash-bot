"""
This module provides a PyMemuc singleton instance.
"""

import sys

from pymemuc import PyMemuc

FROZEN = True #getattr(sys, "frozen", False)

pmc = PyMemuc(debug=not FROZEN)
