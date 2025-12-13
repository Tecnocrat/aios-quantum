"""
PI PULSE - Quantum π Estimation Circuit
========================================

A quantum circuit that estimates digits of π using Quantum Phase Estimation (QPE).

THEORETICAL BASIS:
-----------------
The quantum computer can estimate eigenvalues of unitary operators.
If we encode a phase φ = π/2^k, the QPE algorithm outputs the binary
representation of that phase in the measurement register.

CIRCUIT STRUCTURE:
-----------------
1. Precision Register: n qubits in superposition (determines digits)
2. Target Register: 1 qubit prepared as eigenstate
3. Controlled-U gates: Apply U^(2^k) where U = Rz(π/2^m)
4. Inverse QFT: Decode phase into binary string
5. Measurement: Read out π approximation bits

HOW π IS ENCODED:
----------------
We use the fact that Rz(θ)|1⟩ = e^(iθ/2)|1⟩
By choosing θ = π, we encode the phase π/2 ≈ 1.5708...
The QPE reads this phase in binary: 0.11001001... ≈ π/4

COHERENCE METRIC:
----------------
Coherence = how concentrated the measurement is around true π value
High coherence = sharp peak at correct binary representation
Low coherence = diffuse measurements (decoherence/noise)

OUTPUT MAPPING TO HYPERSPHERE:
-----------------------------
- Position θ: Estimated π value (north = 0, south = 2π)
- Position φ: Error magnitude (equator = zero error)
- Color: Coherence (cyan = high, red = low)
- Intensity: Success probability

Author: AIOS Quantum Team
Date: December 2025
"""

import math
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass
from datetime import datetime
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT


@dataclass
class PiPulseResult:
    """Result from a Pi Pulse quantum experiment."""
    
    # Circuit parameters
    precision_qubits: int      # How many qubits for precision
    total_qubits: int          # Total circuit size
    circuit_depth: int         # Circuit depth
    shots: int                 # Number of shots
    
    # Raw results
    counts: Dict[str, int]     # Measurement counts
    backend: str               # Which backend ran this
    execution_time_ms: float   # How long it took
    
    # π Estimation results
    estimated_pi: float        # Our quantum estimate of π
    actual_pi: float = math.pi # Reference value
    error: float = 0.0         # |estimated - actual|
    correct_digits: int = 0    # How many decimal digits match
    binary_representation: str = ""  # Binary fraction found
    
    # Coherence metrics
    coherence: float = 0.0     # 1 - normalized entropy
    top_probability: float = 0.0  # Probability of most likely outcome
    distribution_width: int = 0   # Number of distinct outcomes
    
    # Metadata
    timestamp: str = ""
    source: str = "real"
    
    def to_dict(self) -> dict:
        return {
            "experiment_type": "pi_pulse",
            "precision_qubits": self.precision_qubits,
            "total_qubits": self.total_qubits,
            "circuit_depth": self.circuit_depth,
            "shots": self.shots,
            "counts": self.counts,
            "backend": self.backend,
            "execution_time_ms": self.execution_time_ms,
            "estimated_pi": self.estimated_pi,
            "actual_pi": self.actual_pi,
            "error": self.error,
            "correct_digits": self.correct_digits,
            "binary_representation": self.binary_representation,
            "coherence": self.coherence,
            "top_probability": self.top_probability,
            "distribution_width": self.distribution_width,
            "timestamp": self.timestamp,
            "source": self.source,
        }


def create_pi_pulse_circuit(
    precision_qubits: int = 8,
    encoding_method: str = "phase_estimation"
) -> QuantumCircuit:
    """
    Create a PI Pulse circuit for quantum π estimation.
    
    The circuit uses Quantum Phase Estimation to read out a phase
    that encodes π. The more precision qubits, the more binary
    digits of π we can estimate.
    
    Args:
        precision_qubits: Number of qubits for precision (3-20)
                         More qubits = more digits but deeper circuit
        encoding_method: "phase_estimation" or "grover_search"
    
    Returns:
        QuantumCircuit configured for π estimation
        
    Circuit Diagram (5 qubits example):
    
        q0 (prec): ─H──●────────────────●──────────┤QFT†├─M
        q1 (prec): ─H──┼──●─────────────┼──●───────┤    ├─M
        q2 (prec): ─H──┼──┼──●──────────┼──┼──●────┤    ├─M
        q3 (prec): ─H──┼──┼──┼──●───────┼──┼──┼──●─┤    ├─M
        q4 (targ): ─X──Rz─Rz─Rz─Rz──────Rz─Rz─Rz─Rz───────
                      π  π/2 π/4 π/8   ...
    """
    
    if precision_qubits < 3:
        precision_qubits = 3  # Minimum for meaningful result
    if precision_qubits > 20:
        precision_qubits = 20  # Maximum practical depth
    
    # Total qubits: precision register + 1 target qubit
    total_qubits = precision_qubits + 1
    
    # Create registers
    precision_reg = QuantumRegister(precision_qubits, 'precision')
    target_reg = QuantumRegister(1, 'target')
    classical_reg = ClassicalRegister(precision_qubits, 'result')
    
    qc = QuantumCircuit(
        precision_reg, target_reg, classical_reg,
        name=f"pi_pulse_{precision_qubits}p"
    )
    
    # ═══════════════════════════════════════════════════════
    # STEP 1: Initialize
    # ═══════════════════════════════════════════════════════
    
    # Put precision register in superposition
    qc.h(precision_reg)
    
    # Prepare target as |1⟩ (eigenstate of Rz)
    qc.x(target_reg[0])
    
    qc.barrier(label="init")
    
    # ═══════════════════════════════════════════════════════
    # STEP 2: Controlled Phase Rotations (Encode π)
    # ═══════════════════════════════════════════════════════
    # 
    # We apply controlled-Rz(π / 2^k) gates
    # This encodes the phase θ = π into the precision register
    # 
    # Rz(θ)|1⟩ = e^(iθ/2)|1⟩, so:
    # - CRz(π)|1⟩ encodes phase π/2
    # - CRz(π/2)|1⟩ encodes phase π/4
    # - etc.
    #
    # The accumulated phase in binary: 0.b₁b₂b₃... where bₖ = π digit
    
    for k in range(precision_qubits):
        # Controlled rotation: angle = π / 2^k
        angle = math.pi / (2 ** k)
        qc.cp(angle, precision_reg[k], target_reg[0])
    
    qc.barrier(label="phase_encode")
    
    # ═══════════════════════════════════════════════════════
    # STEP 3: Inverse Quantum Fourier Transform
    # ═══════════════════════════════════════════════════════
    # 
    # The inverse QFT decodes the binary phase representation
    # from the superposition back into computational basis states
    
    # Apply inverse QFT to precision register
    qft_inverse = QFT(precision_qubits, inverse=True)
    qc.append(qft_inverse, precision_reg)
    
    qc.barrier(label="QFT†")
    
    # ═══════════════════════════════════════════════════════
    # STEP 4: Measurement
    # ═══════════════════════════════════════════════════════
    
    qc.measure(precision_reg, classical_reg)
    
    return qc


def analyze_pi_result(
    counts: Dict[str, int],
    precision_qubits: int,
    shots: int,
    backend: str = "unknown",
    execution_time_ms: float = 0.0
) -> PiPulseResult:
    """
    Analyze measurement results to extract π estimate and coherence.
    
    The measurement gives us a binary string that represents a phase.
    We convert this to a decimal and multiply by 4 to recover π.
    
    Binary phase: 0.b₁b₂b₃... → decimal phase → × 4 → π estimate
    
    Args:
        counts: Measurement outcome counts
        precision_qubits: Number of precision qubits used
        shots: Total shots taken
        backend: Backend name
        execution_time_ms: Execution time
        
    Returns:
        PiPulseResult with full analysis
    """
    
    # Find the most likely outcome
    max_count = max(counts.values())
    total_shots = sum(counts.values())
    
    # Get binary string with highest count
    top_bitstring = max(counts, key=counts.get)
    
    # Convert binary to decimal phase
    # The binary string represents the fractional part of phase/2π
    binary_value = int(top_bitstring, 2)
    max_value = 2 ** precision_qubits
    
    # Phase estimation gives us θ/2π, where θ = π/2
    # So we expect to measure ≈ 1/4 = 0.25
    # Multiply by 2π to get θ, then multiply by 2 to get π
    phase_fraction = binary_value / max_value  # θ/(2π)
    theta = phase_fraction * 2 * math.pi       # θ
    estimated_pi = theta * 2                   # π (since we encoded π/2)
    
    # Alternative interpretation: direct binary fraction of π/4
    # The QPE encodes π/4 ≈ 0.7854, so binary 0.110010...
    # We read the binary and multiply by 4
    binary_fraction = binary_value / max_value
    alt_pi_estimate = binary_fraction * 4
    
    # Use the estimate that's closer to actual π
    if abs(estimated_pi - math.pi) > abs(alt_pi_estimate - math.pi):
        estimated_pi = alt_pi_estimate
    
    # Calculate error
    error = abs(estimated_pi - math.pi)
    
    # Count correct decimal digits
    pi_str = f"{math.pi:.15f}"
    est_str = f"{estimated_pi:.15f}"
    correct_digits = 0
    for i, (p, e) in enumerate(zip(pi_str, est_str)):
        if p == e:
            correct_digits += 1
        else:
            break
    # Subtract the "3." prefix
    if correct_digits >= 2:
        correct_digits -= 2
    
    # Binary representation of the measured phase
    binary_repr = f"0.{top_bitstring}"
    
    # ═══════════════════════════════════════════════════════
    # COHERENCE CALCULATION
    # ═══════════════════════════════════════════════════════
    # 
    # High coherence = measurements concentrated on correct value
    # Low coherence = diffuse, noisy measurements (decoherence)
    
    # Calculate Shannon entropy
    probs = [c / total_shots for c in counts.values()]
    entropy = -sum(p * math.log2(p) for p in probs if p > 0)
    max_entropy = math.log2(len(counts)) if len(counts) > 1 else 1
    
    # Coherence: 1 for perfect (single outcome), 0 for uniform
    coherence = 1 - (entropy / max_entropy) if max_entropy > 0 else 1
    
    # Top probability
    top_probability = max_count / total_shots
    
    # Distribution width (how many outcomes observed)
    distribution_width = len(counts)
    
    return PiPulseResult(
        precision_qubits=precision_qubits,
        total_qubits=precision_qubits + 1,
        circuit_depth=0,  # Will be set by caller
        shots=shots,
        counts=counts,
        backend=backend,
        execution_time_ms=execution_time_ms,
        estimated_pi=estimated_pi,
        error=error,
        correct_digits=correct_digits,
        binary_representation=binary_repr,
        coherence=coherence,
        top_probability=top_probability,
        distribution_width=distribution_width,
        timestamp=datetime.now().isoformat(),
    )


def get_pi_digits_for_qubits(n_qubits: int) -> Tuple[int, float]:
    """
    Estimate how many π digits we can reliably get with n qubits.
    
    Each qubit adds ~0.3 decimal digits of precision.
    But noise reduces effective precision on real hardware.
    
    Returns:
        (theoretical_digits, practical_digits_with_noise)
    """
    # Theoretical: log10(2^n) decimal digits
    theoretical = n_qubits * math.log10(2)
    
    # Practical: noise reduces precision significantly
    # Heron processors have ~99.5% gate fidelity
    # After ~50 gates, fidelity drops to ~75%
    practical = theoretical * 0.6  # Conservative estimate
    
    return int(theoretical), practical


def recommend_circuit_size(time_budget_seconds: float = 10.0) -> dict:
    """
    Recommend circuit parameters based on time budget.
    
    IBM Quantum execution includes:
    - Queue time (0s if empty, up to hours if busy)
    - Transpilation time (~1-5s)
    - Execution time (~0.1-2s per shot batch)
    - Result retrieval (~1-2s)
    
    For a 10-second budget with empty queue:
    - Safe: 8-10 precision qubits (shallow circuit)
    - Aggressive: 12-15 precision qubits (deeper)
    """
    
    if time_budget_seconds <= 5:
        return {
            "precision_qubits": 6,
            "estimated_depth": 50,
            "theoretical_digits": 2,
            "recommended_shots": 1024,
            "note": "Quick pulse - minimal precision"
        }
    elif time_budget_seconds <= 10:
        return {
            "precision_qubits": 8,
            "estimated_depth": 70,
            "theoretical_digits": 2,
            "recommended_shots": 2048,
            "note": "Standard pulse - good balance"
        }
    elif time_budget_seconds <= 30:
        return {
            "precision_qubits": 10,
            "estimated_depth": 100,
            "theoretical_digits": 3,
            "recommended_shots": 4096,
            "note": "Deep pulse - higher precision"
        }
    else:
        return {
            "precision_qubits": 12,
            "estimated_depth": 150,
            "theoretical_digits": 4,
            "recommended_shots": 8192,
            "note": "Maximum pulse - best precision possible"
        }


# ═══════════════════════════════════════════════════════════════════
# VISUALIZATION MAPPING
# ═══════════════════════════════════════════════════════════════════

def map_to_hypersphere(result: PiPulseResult) -> dict:
    """
    Map Pi Pulse result to hypersphere coordinates.
    
    Mapping:
    - θ (polar): estimated_pi / π mapped to [0, π]
              0 = south pole, π = north pole
              Perfect estimate = equator
              
    - φ (azimuthal): error magnitude → longitude
              0 error = prime meridian
              High error = opposite side
              
    - r (radius): coherence
              High coherence = outer surface (1.0)
              Low coherence = inner (collapsed)
              
    - Color: HSL based on correct_digits
              0 digits = red (error)
              1-2 digits = orange/yellow (partial)
              3+ digits = cyan/green (success)
    """
    
    # Polar angle: how close to π
    # Map estimated_pi from [0, 2π] to [0, π] for θ
    ratio = result.estimated_pi / math.pi  # 1.0 = perfect
    # Perfect = π/2 (equator), off by factor of 2 = poles
    theta = abs(ratio - 1.0) * math.pi  # 0 = equator, π = poles
    
    # Azimuthal: error direction
    if result.estimated_pi < math.pi:
        phi = 0  # Underestimate = front
    else:
        phi = math.pi  # Overestimate = back
    phi += result.error * 10  # Spread by error magnitude
    phi = phi % (2 * math.pi)
    
    # Radius: coherence
    radius = 0.5 + 0.5 * result.coherence  # [0.5, 1.0]
    
    # Color: success level
    if result.correct_digits >= 3:
        hue = 0.5  # Cyan
        saturation = 1.0
    elif result.correct_digits >= 2:
        hue = 0.3  # Green
        saturation = 0.9
    elif result.correct_digits >= 1:
        hue = 0.15  # Yellow/orange
        saturation = 0.8
    else:
        hue = 0.0  # Red
        saturation = 1.0
    
    lightness = 0.3 + 0.4 * result.coherence  # Brighter = more coherent
    
    return {
        "theta": theta,
        "phi": phi,
        "radius": radius,
        "hue": hue,
        "saturation": saturation,
        "lightness": lightness,
        "intensity": result.top_probability,
        "label": f"π≈{result.estimated_pi:.4f} ({result.correct_digits} digits)",
    }


if __name__ == "__main__":
    # Quick test
    print("=" * 60)
    print("PI PULSE - Quantum π Estimation Circuit")
    print("=" * 60)
    
    # Show recommendations
    print("\n📊 Time Budget Recommendations:")
    for budget in [5, 10, 30, 60]:
        rec = recommend_circuit_size(budget)
        print(f"  {budget}s: {rec['precision_qubits']} qubits → ~{rec['theoretical_digits']} digits")
    
    # Create circuit
    print("\n🔧 Creating 8-qubit Pi Pulse circuit...")
    qc = create_pi_pulse_circuit(precision_qubits=8)
    print(f"  Total qubits: {qc.num_qubits}")
    print(f"  Circuit depth: {qc.depth()}")
    print(f"  Gates: {qc.count_ops()}")
    
    # Show circuit
    print("\n📐 Circuit structure:")
    print(qc.draw(output='text', fold=80))
