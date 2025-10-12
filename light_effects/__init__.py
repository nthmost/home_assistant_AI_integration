"""
Light Effects Library for Home Assistant

A comprehensive Python library for creating dynamic light effects
with Home Assistant-controlled lights.
"""

from .ha_client import HomeAssistantClient, LightEffects, COLORS, GRADIENTS
from .advanced_effects import AdvancedEffects

__all__ = [
    'HomeAssistantClient',
    'LightEffects',
    'AdvancedEffects',
    'COLORS',
    'GRADIENTS',
]

__version__ = '0.1.0'
