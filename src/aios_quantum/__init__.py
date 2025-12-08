"""
AIOS Quantum - Quantum Computing Integration for AIOS

This package provides quantum computing capabilities using IBM Quantum Platform
and Qiskit Runtime for the AIOS project.
"""

__version__ = "0.1.0"
__author__ = "Tecnocrat"

from .config import QuantumConfig
from .runtime import QuantumRuntime

__all__ = ["QuantumConfig", "QuantumRuntime", "__version__"]
