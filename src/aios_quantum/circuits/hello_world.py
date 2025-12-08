"""
Basic quantum circuits for testing and demonstration.
Based on IBM Quantum Hello World tutorial.
"""

from qiskit import QuantumCircuit
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager


def create_bell_state() -> QuantumCircuit:
    """
    Create a Bell state (maximally entangled 2-qubit state).
    
    Creates the state: |Φ+⟩ = (|00⟩ + |11⟩) / √2
    
    Returns:
        QuantumCircuit representing the Bell state preparation
    """
    qc = QuantumCircuit(2)
    qc.h(0)  # Hadamard on qubit 0
    qc.cx(0, 1)  # CNOT with control=0, target=1
    qc.measure_all()
    return qc


def create_ghz_state(num_qubits: int = 3) -> QuantumCircuit:
    """
    Create a GHZ (Greenberger-Horne-Zeilinger) state.
    
    Creates the state: (|00...0⟩ + |11...1⟩) / √2
    
    Args:
        num_qubits: Number of qubits (default: 3)
        
    Returns:
        QuantumCircuit representing the GHZ state preparation
    """
    if num_qubits < 2:
        raise ValueError("GHZ state requires at least 2 qubits")
    
    qc = QuantumCircuit(num_qubits)
    qc.h(0)  # Hadamard on first qubit
    
    # Chain of CNOTs
    for i in range(num_qubits - 1):
        qc.cx(i, i + 1)
    
    qc.measure_all()
    return qc


def transpile_for_backend(circuit: QuantumCircuit, backend) -> QuantumCircuit:
    """
    Transpile a circuit for a specific backend.
    
    Args:
        circuit: The quantum circuit to transpile
        backend: Target backend
        
    Returns:
        Transpiled circuit optimized for the backend
    """
    pass_manager = generate_preset_pass_manager(
        backend=backend,
        optimization_level=1,
    )
    return pass_manager.run(circuit)
