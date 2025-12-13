"""
EXOTIC QUANTUM EXPERIMENTS
==========================

A collection of unusual quantum circuits for exploration:

1. PI_SEARCH: Search for digits of π using quantum superposition
2. ARITHMETIC: Quantum addition and multiplication
3. ENTANGLEMENT_WITNESS: Detect and measure entanglement
4. GOLDEN_RATIO: Fibonacci-inspired quantum patterns
5. RANDOM_ORACLE: True quantum random number generation

Each experiment produces results that can be mapped to the
hypersphere surface with unique geometric signatures.
"""

import math
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from datetime import datetime

try:
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    from qiskit.circuit.library import QFT, GroverOperator
    from qiskit_ibm_runtime import SamplerV2 as Sampler
    from qiskit_aer import AerSimulator
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    print("Warning: Qiskit not available. Exotic experiments will use mock data.")


@dataclass
class ExoticResult:
    """Result from an exotic quantum experiment."""
    experiment_type: str
    experiment_id: str
    counts: Dict[str, int]
    timestamp: str
    n_qubits: int
    n_shots: int
    circuit_depth: int
    backend: str
    
    # Computed metrics
    coherence: float = 0.0
    entropy: float = 0.0
    target_value: Optional[Any] = None  # What we were searching for
    found_value: Optional[Any] = None   # What we found
    success_probability: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "experiment_type": self.experiment_type,
            "id": self.experiment_id,
            "counts": self.counts,
            "timestamp": self.timestamp,
            "n_qubits": self.n_qubits,
            "n_shots": self.n_shots,
            "circuit_depth": self.circuit_depth,
            "backend": self.backend,
            "coherence": self.coherence,
            "entropy": self.entropy,
            "target_value": self.target_value,
            "found_value": self.found_value,
            "success_probability": self.success_probability,
        }


# ═══════════════════════════════════════════════════════════════════
# PI SEARCH EXPERIMENT
# Uses Grover's algorithm to search for binary representations of π digits
# ═══════════════════════════════════════════════════════════════════

def create_pi_oracle(n_qubits: int, digit_index: int = 0) -> QuantumCircuit:
    """Create an oracle that marks states matching π digits.
    
    π = 3.14159265358979...
    We encode digits as binary and mark them in superposition.
    
    Args:
        n_qubits: Number of qubits (determines precision)
        digit_index: Which digit of π to search for (0=3, 1=1, 2=4, etc.)
    
    Returns:
        Oracle circuit that marks π digit states
    """
    if not QISKIT_AVAILABLE:
        return None
    
    # Get π digits: 3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9...
    pi_digits = [int(d) for d in "314159265358979323846"[:n_qubits * 2]]
    
    # Get the target digit
    target = pi_digits[digit_index % len(pi_digits)]
    
    # Create oracle circuit
    qc = QuantumCircuit(n_qubits, name=f"π_oracle_{digit_index}")
    
    # Mark states where measurement equals target digit
    # For simplicity, we use a phase flip on states matching target
    target_binary = format(target, f'0{n_qubits}b')
    
    # Apply X gates to flip qubits that should be 0 in target
    for i, bit in enumerate(target_binary):
        if bit == '0':
            qc.x(i)
    
    # Multi-controlled Z gate (marks target state with -1 phase)
    if n_qubits == 1:
        qc.z(0)
    elif n_qubits == 2:
        qc.cz(0, 1)
    else:
        # Use multi-controlled Z for larger circuits
        qc.h(n_qubits - 1)
        qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
        qc.h(n_qubits - 1)
    
    # Undo X gates
    for i, bit in enumerate(target_binary):
        if bit == '0':
            qc.x(i)
    
    return qc


def pi_search_circuit(n_qubits: int = 4, iterations: int = 1) -> QuantumCircuit:
    """Create Grover search circuit for π digits.
    
    Args:
        n_qubits: Number of qubits (4 gives 4 bits precision)
        iterations: Number of Grover iterations
    
    Returns:
        Complete search circuit
    """
    if not QISKIT_AVAILABLE:
        return None
    
    qc = QuantumCircuit(n_qubits, n_qubits, name="pi_search")
    
    # Initial superposition
    qc.h(range(n_qubits))
    
    # Grover iterations
    for i in range(iterations):
        # Oracle (marks π digits)
        oracle = create_pi_oracle(n_qubits, digit_index=i % 10)
        qc.compose(oracle, inplace=True)
        
        # Diffusion operator
        qc.h(range(n_qubits))
        qc.x(range(n_qubits))
        
        # Multi-controlled Z
        qc.h(n_qubits - 1)
        qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
        qc.h(n_qubits - 1)
        
        qc.x(range(n_qubits))
        qc.h(range(n_qubits))
    
    # Measure
    qc.measure(range(n_qubits), range(n_qubits))
    
    return qc


# ═══════════════════════════════════════════════════════════════════
# QUANTUM ARITHMETIC
# Addition and multiplication in superposition
# ═══════════════════════════════════════════════════════════════════

def quantum_adder_circuit(a_bits: int = 2, b_bits: int = 2) -> QuantumCircuit:
    """Create quantum ripple-carry adder circuit.
    
    Adds two numbers in superposition: |a⟩|b⟩ → |a⟩|a+b⟩
    
    Args:
        a_bits: Bits for first number
        b_bits: Bits for second number (result stored here)
    
    Returns:
        Adder circuit
    """
    if not QISKIT_AVAILABLE:
        return None
    
    n_qubits = a_bits + b_bits + 1  # +1 for carry
    qc = QuantumCircuit(n_qubits, b_bits + 1, name="quantum_add")
    
    # Prepare superposition of inputs
    # a register: qubits 0 to a_bits-1
    # b register: qubits a_bits to a_bits+b_bits-1
    # carry: last qubit
    
    qc.h(range(a_bits))  # Superposition of a
    qc.h(range(a_bits, a_bits + b_bits))  # Superposition of b
    
    # Ripple carry addition
    for i in range(min(a_bits, b_bits)):
        a_idx = i
        b_idx = a_bits + i
        carry_in = n_qubits - 1 if i == 0 else a_bits + b_bits
        
        # Full adder
        qc.ccx(a_idx, b_idx, carry_in)  # AND gate for carry
        qc.cx(a_idx, b_idx)  # XOR for sum
    
    # Measure result (b register now contains a+b)
    qc.measure(range(a_bits, a_bits + b_bits + 1), range(b_bits + 1))
    
    return qc


def quantum_multiplier_circuit(n_bits: int = 2) -> QuantumCircuit:
    """Create quantum multiplication circuit.
    
    Multiplies two numbers using repeated addition.
    
    Args:
        n_bits: Bits per number
    
    Returns:
        Multiplier circuit
    """
    if not QISKIT_AVAILABLE:
        return None
    
    # Need: a register, b register, result register (2*n_bits)
    n_qubits = n_bits + n_bits + 2 * n_bits
    qc = QuantumCircuit(n_qubits, 2 * n_bits, name="quantum_mult")
    
    # Prepare inputs in superposition
    qc.h(range(n_bits))  # a
    qc.h(range(n_bits, 2 * n_bits))  # b
    
    # Simplified multiplication using controlled additions
    # This is a proof-of-concept, not a full multiplier
    for i in range(n_bits):
        for j in range(n_bits):
            # Controlled AND: add a[i] * b[j] to result[i+j]
            ctrl_a = i
            ctrl_b = n_bits + j
            target = 2 * n_bits + i + j
            if target < n_qubits:
                qc.ccx(ctrl_a, ctrl_b, target)
    
    # Measure result
    qc.measure(range(2 * n_bits, n_qubits), range(2 * n_bits))
    
    return qc


# ═══════════════════════════════════════════════════════════════════
# ENTANGLEMENT WITNESS
# Detect and quantify entanglement
# ═══════════════════════════════════════════════════════════════════

def bell_state_circuit(state_type: str = "phi+") -> QuantumCircuit:
    """Create a Bell state (maximally entangled 2-qubit state).
    
    Args:
        state_type: "phi+", "phi-", "psi+", or "psi-"
    
    Returns:
        Bell state preparation circuit
    """
    if not QISKIT_AVAILABLE:
        return None
    
    qc = QuantumCircuit(2, 2, name=f"bell_{state_type}")
    
    # Create |Φ+⟩ = (|00⟩ + |11⟩)/√2
    qc.h(0)
    qc.cx(0, 1)
    
    # Modify for other Bell states
    if state_type == "phi-":
        qc.z(0)  # |Φ-⟩ = (|00⟩ - |11⟩)/√2
    elif state_type == "psi+":
        qc.x(1)  # |Ψ+⟩ = (|01⟩ + |10⟩)/√2
    elif state_type == "psi-":
        qc.z(0)
        qc.x(1)  # |Ψ-⟩ = (|01⟩ - |10⟩)/√2
    
    qc.measure([0, 1], [0, 1])
    
    return qc


def ghz_state_circuit(n_qubits: int = 3) -> QuantumCircuit:
    """Create GHZ state (generalized Bell state for n qubits).
    
    |GHZ⟩ = (|00...0⟩ + |11...1⟩)/√2
    
    Args:
        n_qubits: Number of qubits
    
    Returns:
        GHZ state circuit
    """
    if not QISKIT_AVAILABLE:
        return None
    
    qc = QuantumCircuit(n_qubits, n_qubits, name=f"ghz_{n_qubits}")
    
    # Create superposition on first qubit
    qc.h(0)
    
    # Entangle all others with CNOT chain
    for i in range(n_qubits - 1):
        qc.cx(i, i + 1)
    
    qc.measure(range(n_qubits), range(n_qubits))
    
    return qc


def entanglement_witness_circuit(n_qubits: int = 4) -> QuantumCircuit:
    """Create entanglement witness measurement circuit.
    
    Measures correlations that can only exist with entanglement.
    
    Args:
        n_qubits: Number of qubits
    
    Returns:
        Witness measurement circuit
    """
    if not QISKIT_AVAILABLE:
        return None
    
    qc = QuantumCircuit(n_qubits, n_qubits, name="entanglement_witness")
    
    # Create cluster state (highly entangled)
    qc.h(range(n_qubits))
    
    # Apply CZ gates in a pattern
    for i in range(n_qubits - 1):
        qc.cz(i, i + 1)
    # Close the loop
    if n_qubits > 2:
        qc.cz(n_qubits - 1, 0)
    
    # Random local rotations (to probe entanglement)
    for i in range(n_qubits):
        angle = math.pi * (i + 1) / n_qubits
        qc.ry(angle, i)
    
    qc.measure(range(n_qubits), range(n_qubits))
    
    return qc


# ═══════════════════════════════════════════════════════════════════
# GOLDEN RATIO EXPERIMENT
# Fibonacci-inspired quantum patterns
# ═══════════════════════════════════════════════════════════════════

def golden_ratio_circuit(n_qubits: int = 5) -> QuantumCircuit:
    """Create circuit encoding golden ratio patterns.
    
    Uses Fibonacci sequence to determine rotation angles.
    φ = (1 + √5) / 2 ≈ 1.618
    
    Args:
        n_qubits: Number of qubits
    
    Returns:
        Golden ratio circuit
    """
    if not QISKIT_AVAILABLE:
        return None
    
    phi = (1 + math.sqrt(5)) / 2  # Golden ratio
    
    qc = QuantumCircuit(n_qubits, n_qubits, name="golden_ratio")
    
    # Initial superposition
    qc.h(range(n_qubits))
    
    # Fibonacci sequence: 1, 1, 2, 3, 5, 8, 13, 21...
    fib = [1, 1]
    while len(fib) < n_qubits:
        fib.append(fib[-1] + fib[-2])
    
    # Apply rotations based on Fibonacci ratios
    for i in range(n_qubits):
        # Rotation angle approaches φ as i increases
        angle = 2 * math.pi * fib[i] / fib[-1]
        qc.rz(angle, i)
        qc.ry(angle / phi, i)
    
    # Entangle using golden angle
    golden_angle = 2 * math.pi / (phi ** 2)
    for i in range(n_qubits - 1):
        qc.crz(golden_angle, i, i + 1)
    
    # Final layer
    qc.h(range(n_qubits))
    
    qc.measure(range(n_qubits), range(n_qubits))
    
    return qc


# ═══════════════════════════════════════════════════════════════════
# QUANTUM RANDOM NUMBER GENERATOR
# True quantum randomness
# ═══════════════════════════════════════════════════════════════════

def qrng_circuit(n_bits: int = 8) -> QuantumCircuit:
    """Generate true random numbers using quantum mechanics.
    
    The uncertainty principle guarantees these are truly random.
    
    Args:
        n_bits: Number of random bits to generate
    
    Returns:
        QRNG circuit
    """
    if not QISKIT_AVAILABLE:
        return None
    
    qc = QuantumCircuit(n_bits, n_bits, name="qrng")
    
    # Hadamard on all qubits creates 50/50 superposition
    qc.h(range(n_bits))
    
    # Measure all qubits
    qc.measure(range(n_bits), range(n_bits))
    
    return qc


# ═══════════════════════════════════════════════════════════════════
# EXPERIMENT RUNNER
# Execute experiments and collect results
# ═══════════════════════════════════════════════════════════════════

def run_exotic_experiment(
    experiment_type: str,
    n_qubits: int = 4,
    n_shots: int = 1024,
    use_simulator: bool = True,
) -> ExoticResult:
    """Run an exotic quantum experiment.
    
    Args:
        experiment_type: One of "pi_search", "arithmetic", "entanglement",
                        "golden_ratio", "random"
        n_qubits: Number of qubits
        n_shots: Number of measurement shots
        use_simulator: Use simulator (True) or real quantum (False)
    
    Returns:
        ExoticResult with experiment data
    """
    timestamp = datetime.now().isoformat()
    experiment_id = f"{experiment_type}_{timestamp.replace(':', '-')}"
    
    # Build circuit based on type
    if experiment_type == "pi_search":
        circuit = pi_search_circuit(n_qubits, iterations=2)
        target_value = 3.14159
    elif experiment_type == "arithmetic":
        circuit = quantum_adder_circuit(n_qubits // 2, n_qubits // 2)
        target_value = "addition"
    elif experiment_type == "entanglement":
        circuit = entanglement_witness_circuit(n_qubits)
        target_value = "witness"
    elif experiment_type == "golden_ratio":
        circuit = golden_ratio_circuit(n_qubits)
        target_value = (1 + math.sqrt(5)) / 2
    elif experiment_type == "random":
        circuit = qrng_circuit(n_qubits)
        target_value = "random"
    elif experiment_type == "bell":
        circuit = bell_state_circuit("phi+")
        n_qubits = 2
        target_value = "entangled"
    elif experiment_type == "ghz":
        circuit = ghz_state_circuit(n_qubits)
        target_value = "GHZ"
    else:
        # Default to random
        circuit = qrng_circuit(n_qubits)
        target_value = "random"
    
    # Run on simulator or return mock data
    if not QISKIT_AVAILABLE or circuit is None:
        # Mock data for when Qiskit isn't available
        import random
        counts = {}
        for _ in range(min(32, 2**n_qubits)):
            state = format(random.randint(0, 2**n_qubits - 1), f'0{n_qubits}b')
            counts[state] = random.randint(1, n_shots // 10)
        
        # Normalize
        total = sum(counts.values())
        scale = n_shots / total
        counts = {k: int(v * scale) for k, v in counts.items()}
        
        backend = "mock_simulator"
        circuit_depth = n_qubits * 3
    else:
        # Run on Aer simulator
        simulator = AerSimulator()
        sampler = Sampler(simulator)
        
        job = sampler.run([circuit], shots=n_shots)
        result = job.result()
        
        # Get counts from result
        pub_result = result[0]
        counts_raw = pub_result.data.meas.get_counts()
        counts = dict(counts_raw)
        
        backend = "aer_simulator"
        circuit_depth = circuit.depth()
    
    # Compute metrics
    total = sum(counts.values())
    probs = [c / total for c in counts.values()]
    coherence = max(probs)
    entropy = -sum(p * math.log2(p) for p in probs if p > 0)
    
    # Find most likely result
    dominant_state = max(counts, key=counts.get)
    found_value = int(dominant_state, 2)
    success_prob = counts[dominant_state] / total
    
    return ExoticResult(
        experiment_type=experiment_type,
        experiment_id=experiment_id,
        counts=counts,
        timestamp=timestamp,
        n_qubits=n_qubits,
        n_shots=n_shots,
        circuit_depth=circuit_depth,
        backend=backend,
        coherence=coherence,
        entropy=entropy,
        target_value=target_value,
        found_value=found_value,
        success_probability=success_prob,
    )


def run_all_exotic_experiments(
    n_qubits: int = 4,
    n_shots: int = 1024,
) -> List[ExoticResult]:
    """Run all exotic experiments and return results.
    
    Args:
        n_qubits: Number of qubits for each experiment
        n_shots: Shots per experiment
    
    Returns:
        List of all experiment results
    """
    experiments = [
        "pi_search",
        "arithmetic",
        "entanglement",
        "golden_ratio",
        "random",
        "bell",
        "ghz",
    ]
    
    results = []
    for exp_type in experiments:
        print(f"Running {exp_type}...")
        result = run_exotic_experiment(exp_type, n_qubits, n_shots)
        results.append(result)
        print(f"  Coherence: {result.coherence:.3f}, Entropy: {result.entropy:.3f}")
    
    return results
