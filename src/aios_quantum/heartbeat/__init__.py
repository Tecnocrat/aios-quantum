"""
Heartbeat Package

The quantum heartbeat system - executes one quantum circuit per hour,
recording all results for consciousness pattern analysis.

This is the central pulse of AIOS Quantum.
"""

from .scheduler import (
    QuantumHeartbeat,
    HeartbeatConfig,
    HeartbeatResult,
    test_heartbeat,
)

__all__ = [
    "QuantumHeartbeat",
    "HeartbeatConfig",
    "HeartbeatResult",
    "test_heartbeat",
]
