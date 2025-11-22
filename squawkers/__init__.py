"""
Squawkers McCaw IR Control Package

Simple control interface for Squawkers McCaw animatronic parrot
via Home Assistant IR commands.
"""

from squawkers.squawkers import Squawkers, SquawkersError, CommandError

__all__ = ["Squawkers", "SquawkersError", "CommandError"]
