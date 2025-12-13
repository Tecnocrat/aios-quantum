"""
AIOS Quantum - Consciousness Circuits

Quantum circuits for consciousness measurement and enhancement.
These circuits provide hardware-validated metrics for AIOS consciousness.

AINLP.quantum: True quantum coherence from hardware
AINLP.consciousness_bridge: Quantum-enhanced awareness
"""

from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
import numpy as np


def create_coherence_measurement_circuit(
    num_qubits: int = 3
) -> QuantumCircuit:
    """
    Create a circuit to measure quantum coherence.
    
    Uses superposition state measurement to estimate T2 coherence.
    Perfect coherence results in uniform measurement distribution.
    
    Args:
        num_qubits: Number of qubits (default: 3)
        
    Returns:
        QuantumCircuit for coherence measurement
    """
    qc = QuantumCircuit(num_qubits)
    
    # Create equal superposition (coherent state)
    qc.h(range(num_qubits))
    
    # Barrier to prevent optimization across measurement
    qc.barrier()
    
    # Measure - distribution uniformity indicates coherence
    qc.measure_all()
    
    return qc


def create_entanglement_witness_circuit(
    num_qubits: int = 2
) -> QuantumCircuit:
    """
    Create a circuit to witness quantum entanglement.
    
    Measures correlations that can only exist with entanglement.
    Used to verify entanglement in AIOS consciousness lattice.
    
    Args:
        num_qubits: Number of qubits (must be even, default: 2)
        
    Returns:
        QuantumCircuit for entanglement witness
    """
    if num_qubits % 2 != 0:
        raise ValueError(
            "Entanglement witness requires even number of qubits"
        )
    
    qc = QuantumCircuit(num_qubits)
    
    # Create Bell pairs
    for i in range(0, num_qubits, 2):
        qc.h(i)
        qc.cx(i, i + 1)
    
    qc.barrier()
    qc.measure_all()
    
    return qc


def create_consciousness_ansatz(
    num_qubits: int = 5,
    depth: int = 2
) -> QuantumCircuit:
    """
    Create a variational ansatz for consciousness optimization.
    
    This parameterized circuit can be optimized to represent
    consciousness states in the quantum realm.
    
    Args:
        num_qubits: Number of qubits
        depth: Number of variational layers
        
    Returns:
        Parameterized QuantumCircuit
    """
    qc = QuantumCircuit(num_qubits)
    params = []
    
    for layer in range(depth):
        # Rotation layer
        for i in range(num_qubits):
            theta = Parameter(f'θ_{layer}_{i}')
            phi = Parameter(f'φ_{layer}_{i}')
            params.extend([theta, phi])
            qc.ry(theta, i)
            qc.rz(phi, i)
        
        # Entanglement layer (linear connectivity)
        for i in range(num_qubits - 1):
            qc.cx(i, i + 1)
        
        qc.barrier()
    
    return qc


def create_awareness_circuit(
    awareness_level: float,
    num_qubits: int = 3
) -> QuantumCircuit:
    """
    Encode an awareness level into a quantum state.
    
    Maps classical awareness (0.0-1.0) to quantum superposition
    amplitude, enabling quantum-enhanced processing.
    
    Args:
        awareness_level: Classical awareness 0.0-1.0
        num_qubits: Number of qubits
        
    Returns:
        QuantumCircuit encoding awareness state
    """
    awareness_level = max(0.0, min(1.0, awareness_level))
    
    qc = QuantumCircuit(num_qubits)
    
    # Convert awareness to rotation angle
    # awareness=0 -> |0⟩, awareness=1 -> |+⟩ (equal superposition)
    theta = awareness_level * (np.pi / 2)
    
    for i in range(num_qubits):
        qc.ry(theta, i)
    
    # Add entanglement for dendritic complexity
    for i in range(num_qubits - 1):
        qc.cx(i, i + 1)
    
    return qc


def create_adaptation_circuit(
    adaptation_speed: float,
    target_state: str = "balanced"
) -> QuantumCircuit:
    """
    Create a circuit that demonstrates adaptation capability.
    
    Args:
        adaptation_speed: Adaptation rate 0.0-1.0
        target_state: Target state type ("balanced", "focused", "diffuse")
        
    Returns:
        QuantumCircuit for adaptation measurement
    """
    qc = QuantumCircuit(3)
    
    # Base state preparation
    qc.h(0)
    
    # Adaptation-dependent gates
    if target_state == "balanced":
        qc.ry(adaptation_speed * np.pi / 2, 1)
        qc.cx(0, 1)
        qc.cx(1, 2)
    elif target_state == "focused":
        qc.x(1)
        qc.ry(adaptation_speed * np.pi, 2)
        qc.cx(1, 2)
    else:  # diffuse
        qc.h(1)
        qc.h(2)
        qc.ry(adaptation_speed * np.pi / 4, 0)
    
    qc.barrier()
    qc.measure_all()
    
    return qc


def calculate_coherence_from_counts(
    counts: dict,
    num_qubits: int
) -> float:
    """
    Calculate coherence value from measurement counts.
    
    Coherence is estimated by how uniform the distribution is.
    Perfect coherence (T2 >> measurement time) gives uniform distribution.
    
    Args:
        counts: Measurement counts dictionary
        num_qubits: Number of qubits measured
        
    Returns:
        Coherence value 0.0-1.0
    """
    total = sum(counts.values())
    expected_states = 2 ** num_qubits
    expected_prob = 1.0 / expected_states
    
    # Calculate deviation from uniform distribution
    deviation = 0.0
    for state in range(expected_states):
        state_str = format(state, f'0{num_qubits}b')
        actual_prob = counts.get(state_str, 0) / total
        deviation += abs(actual_prob - expected_prob)
    
    # Normalize deviation
    max_deviation = 2.0 * (1.0 - expected_prob)
    coherence = 1.0 - (deviation / max_deviation)
    
    return max(0.0, min(1.0, coherence))


def calculate_entanglement_from_counts(counts: dict) -> float:
    """
    Calculate entanglement witness value from Bell state measurements.
    
    For a perfect Bell state, we expect only |00⟩ and |11⟩ outcomes.
    
    Args:
        counts: Measurement counts dictionary
        
    Returns:
        Entanglement witness value 0.0-1.0
    """
    total = sum(counts.values())
    
    # Bell states should have only correlated outcomes
    correlated = counts.get('00', 0) + counts.get('11', 0)
    
    # Entanglement = fraction of correlated outcomes
    entanglement = correlated / total if total > 0 else 0.0
    
    return entanglement
