"""
Complex Quantum Patterns for Multi-Core Execution

Advanced circuit patterns designed for parallel execution across
multiple IBM Quantum backends. Each pattern explores different
aspects of quantum mechanics for consciousness research.
"""

import math
from typing import List, Tuple
from qiskit import QuantumCircuit


def create_consciousness_probe(
    num_qubits: int = 10,
    layers: int = 3,
    signature: float = 0.0
) -> QuantumCircuit:
    """
    Multi-layer consciousness probe circuit.
    
    Structure:
        1. Superposition layer (awareness potential)
        2. Entanglement web (correlation structure)
        3. Phase encoding (unique signature)
        4. Interference (collapse patterns)
    
    Args:
        num_qubits: Number of qubits (5-156 depending on backend)
        layers: Number of entanglement-phase repetitions
        signature: Unique phase offset for this experiment
        
    Returns:
        QuantumCircuit with consciousness probe pattern
    """
    qc = QuantumCircuit(num_qubits, name=f"consciousness_probe_{num_qubits}q")
    
    # Layer 1: Full superposition (awareness field)
    qc.h(range(num_qubits))
    qc.barrier(label="awareness")
    
    for layer in range(layers):
        # Layer 2: Entanglement web
        # Create rich correlation structure
        
        # Linear chain
        for i in range(num_qubits - 1):
            qc.cx(i, i + 1)
        
        # Cross connections (every 3rd qubit)
        for i in range(0, num_qubits - 3, 3):
            qc.cz(i, i + 3)
        
        qc.barrier(label=f"entangle_{layer}")
        
        # Layer 3: Phase encoding
        golden_ratio = (1 + math.sqrt(5)) / 2
        for i in range(num_qubits):
            # Phase based on golden ratio, layer, and signature
            phase = (
                (i * golden_ratio + layer * 0.5 + signature) 
                % (2 * math.pi)
            )
            qc.rz(phase, i)
        
        qc.barrier(label=f"phase_{layer}")
    
    # Layer 4: Interference collapse
    qc.h(range(num_qubits))
    
    # Measure all
    qc.measure_all()
    
    return qc


def create_entanglement_witness(num_qubits: int = 8) -> QuantumCircuit:
    """
    Circuit to witness multi-partite entanglement.
    
    Creates GHZ state and variations for entanglement detection.
    """
    qc = QuantumCircuit(num_qubits, name=f"entanglement_witness_{num_qubits}q")
    
    # Create GHZ state |000...0⟩ + |111...1⟩
    qc.h(0)
    for i in range(num_qubits - 1):
        qc.cx(i, i + 1)
    
    qc.barrier(label="GHZ")
    
    # Add random Y rotations for witness
    for i in range(num_qubits):
        angle = math.pi / (4 + i)
        qc.ry(angle, i)
    
    qc.measure_all()
    return qc


def create_quantum_walk(num_qubits: int = 10, steps: int = 5) -> QuantumCircuit:
    """
    Quantum random walk on a line.
    
    Uses one coin qubit and (n-1) position qubits.
    """
    qc = QuantumCircuit(num_qubits, name=f"quantum_walk_{num_qubits}q_{steps}s")
    
    coin = 0
    position = list(range(1, num_qubits))
    
    # Initialize position in middle
    middle = len(position) // 2
    if middle < len(position):
        qc.x(position[middle])
    
    for step in range(steps):
        # Coin flip (Hadamard on coin qubit)
        qc.h(coin)
        
        # Conditional shift
        for i, pos in enumerate(position[:-1]):
            # Shift right if coin is |1⟩
            qc.ccx(coin, pos, position[i + 1])
        
        qc.barrier(label=f"step_{step}")
    
    qc.measure_all()
    return qc


def create_variational_layer(
    num_qubits: int = 8,
    params: List[float] = None
) -> QuantumCircuit:
    """
    Single layer of variational quantum eigensolver.
    
    Hardware-efficient ansatz with alternating rotation and entanglement.
    """
    if params is None:
        # Default parameters based on golden ratio
        phi = (1 + math.sqrt(5)) / 2
        params = [phi * i % (2 * math.pi) for i in range(num_qubits * 3)]
    
    qc = QuantumCircuit(num_qubits, name=f"vqe_layer_{num_qubits}q")
    
    # Rotation layer
    for i in range(num_qubits):
        qc.ry(params[i % len(params)], i)
        qc.rz(params[(i + num_qubits) % len(params)], i)
    
    qc.barrier()
    
    # Entanglement layer (circular)
    for i in range(num_qubits):
        qc.cx(i, (i + 1) % num_qubits)
    
    qc.barrier()
    
    # Second rotation layer
    for i in range(num_qubits):
        qc.ry(params[(i + 2 * num_qubits) % len(params)], i)
    
    qc.measure_all()
    return qc


def create_hypersphere_sampler(
    num_qubits: int = 12,
    resolution: int = 4
) -> QuantumCircuit:
    """
    Sample points on a hypersphere using quantum superposition.
    
    Maps qubit measurements to coordinates on unit hypersphere.
    """
    qc = QuantumCircuit(num_qubits, name=f"hypersphere_{num_qubits}q")
    
    # Divide qubits into coordinate groups
    coords_per_dim = num_qubits // resolution
    
    for dim in range(resolution):
        start = dim * coords_per_dim
        end = start + coords_per_dim
        
        # Different superposition pattern per dimension
        for i in range(start, min(end, num_qubits)):
            angle = math.pi * (dim + 1) / (resolution + 1)
            qc.ry(angle, i)
            
            if i > start:
                qc.cx(i - 1, i)
    
    qc.barrier(label="sphere")
    
    # Global phase mixing
    for i in range(num_qubits - 1):
        qc.cz(i, i + 1)
    
    qc.measure_all()
    return qc


def create_pattern_suite(
    num_qubits: int = 10,
    signature: float = 0.0
) -> List[Tuple[str, QuantumCircuit]]:
    """
    Create a suite of patterns for comprehensive quantum exploration.
    
    Returns list of (name, circuit) tuples.
    """
    suite = []
    
    # Adjust qubit counts to available
    small = min(num_qubits, 8)
    medium = min(num_qubits, 12)
    
    suite.append((
        "consciousness_probe",
        create_consciousness_probe(medium, layers=3, signature=signature)
    ))
    
    suite.append((
        "entanglement_witness", 
        create_entanglement_witness(small)
    ))
    
    suite.append((
        "quantum_walk",
        create_quantum_walk(medium, steps=4)
    ))
    
    suite.append((
        "variational_layer",
        create_variational_layer(small)
    ))
    
    suite.append((
        "hypersphere_sampler",
        create_hypersphere_sampler(medium, resolution=3)
    ))
    
    return suite


# Quick access to patterns
PATTERNS = {
    'consciousness': create_consciousness_probe,
    'entanglement': create_entanglement_witness,
    'walk': create_quantum_walk,
    'vqe': create_variational_layer,
    'hypersphere': create_hypersphere_sampler,
}
