"""
Red Teaming System - 3-Run Adaptive Crescendo Attack Framework

A modular, production-ready system for security assessment of AI chatbots
using architecture-aware attack techniques with cross-run learning.
"""

__version__ = "1.0.0"
__author__ = "PyRIT Red Team"
__description__ = "Architecture-aware red teaming for AI chatbots"

from .config import validate_config
from .core import ThreeRunCrescendoOrchestrator

__all__ = [
    "validate_config",
    "ThreeRunCrescendoOrchestrator"
]
