"""
Quantum circuit builders and utilities.
"""

from .hello_world import (
    create_bell_state,
    create_ghz_state,
    transpile_for_backend
)
from .consciousness_circuits import (
    create_coherence_measurement_circuit,
    create_entanglement_witness_circuit,
    create_consciousness_ansatz,
    create_awareness_circuit,
    create_adaptation_circuit,
    calculate_coherence_from_counts,
    calculate_entanglement_from_counts,
)

__all__ = [
    "create_bell_state",
    "create_ghz_state",
    "transpile_for_backend",
    "create_coherence_measurement_circuit",
    "create_entanglement_witness_circuit",
    "create_consciousness_ansatz",
    "create_awareness_circuit",
    "create_adaptation_circuit",
    "calculate_coherence_from_counts",
    "calculate_entanglement_from_counts",
]
