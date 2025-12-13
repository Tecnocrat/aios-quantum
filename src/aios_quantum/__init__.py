"""
AIOS Quantum - Quantum Computing Integration for AIOS

This package provides quantum computing capabilities using
IBM Quantum Platform and Qiskit Runtime for the AIOS project.

6th Supercell: Quantum Intelligence
"""

__version__ = "0.1.0"
__author__ = "Tecnocrat"

from .config import QuantumConfig
from .runtime import QuantumRuntime
from .supercell import QuantumSupercell, QuantumSupercellInterface
from .communication import (
    SupercellType,
    MessagePriority,
    CommunicationType,
    QuantumMessage,
    QuantumState,
)
from .about import about, get_info, welcome, print_about

__all__ = [
    "QuantumConfig",
    "QuantumRuntime",
    "QuantumSupercell",
    "QuantumSupercellInterface",
    "SupercellType",
    "MessagePriority",
    "CommunicationType",
    "QuantumMessage",
    "QuantumState",
    "__version__",
    "about",
    "get_info",
    "welcome",
    "print_about",
]
