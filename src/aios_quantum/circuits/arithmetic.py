"""
Quantum Arithmetic Circuits - Basic Math on Quantum Substrate

AINLP Provenance:
  origin: opus (architect)
  created: 2025-12-12
  purpose: Test quantum coherence through simple arithmetic

Theory:
  The simplest arithmetic operations reveal decoherence:
  - How quickly does 1+1 drift from 2?
  - At what depth does counting fail?
  - Can we build a coherence profile from arithmetic errors?
  
  This creates a COHERENCE GRADIENT that can guide runtime routing.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import math

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister


@dataclass
class ArithmeticResult:
    """Result of a quantum arithmetic operation."""
    operation: str
    expected: int
    measured: Dict[str, int]  # All measurement outcomes
    most_likely: int
    accuracy: float  # How often we got the right answer
    error_distribution: Dict[int, float]  # Wrong answers and their frequencies
    circuit_depth: int
    backend: str
    coherence_score: float  # Derived metric
    timestamp: str = ""
    job_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation,
            "expected": self.expected,
            "most_likely": self.most_likely,
            "accuracy": self.accuracy,
            "error_distribution": self.error_distribution,
            "circuit_depth": self.circuit_depth,
            "backend": self.backend,
            "coherence_score": self.coherence_score,
            "timestamp": self.timestamp,
            "job_id": self.job_id,
        }


def create_increment_circuit(n_bits: int = 3, value: int = 0) -> QuantumCircuit:
    """
    Create a circuit that increments a quantum register by 1.
    
    This is COUNTING: value → value + 1
    
    Implementation: Ripple-carry increment (correct version)
    Key insight: We need to flip from MSB down, checking if lower bits will carry.
    
    Algorithm:
    - For n bits, we apply controlled-X gates from MSB to LSB
    - Each bit flips if ALL bits below it are 1
    - Process from MSB down to LSB
    
    Args:
        n_bits: Width of register
        value: Initial value to encode
        
    Returns:
        Circuit that computes value + 1
    """
    qr = QuantumRegister(n_bits, 'q')
    cr = ClassicalRegister(n_bits, 'c')
    qc = QuantumCircuit(qr, cr, name=f"inc_{value}")
    
    # Encode initial value
    for i in range(n_bits):
        if (value >> i) & 1:
            qc.x(qr[i])
    
    qc.barrier()
    
    # Increment operation: process from MSB down to LSB
    # This is the standard quantum increment circuit
    # 
    # For 3 bits (q2, q1, q0):
    #   q2 flips if q1=1 AND q0=1
    #   q1 flips if q0=1
    #   q0 always flips
    #
    # We go from MSB to LSB:
    for i in range(n_bits - 1, -1, -1):
        if i == 0:
            # LSB always flips
            qc.x(qr[0])
        else:
            # Bit i flips if all bits 0..i-1 are 1
            qc.mcx(list(qr[:i]), qr[i])
    
    qc.barrier()
    qc.measure(qr, cr)
    
    return qc


def create_addition_circuit(n_bits: int = 3, a: int = 1, b: int = 1) -> QuantumCircuit:
    """
    Create a circuit that computes a + b.
    
    Simple addition using repeated increment.
    Not efficient, but reveals coherence degradation with depth.
    
    Args:
        n_bits: Width of registers (result needs n_bits for sum)
        a, b: Values to add
        
    Returns:
        Circuit computing a + b
    """
    qr = QuantumRegister(n_bits, 'sum')
    cr = ClassicalRegister(n_bits, 'result')
    qc = QuantumCircuit(qr, cr, name=f"add_{a}_{b}")
    
    # Encode value 'a' into register
    for i in range(n_bits):
        if (a >> i) & 1:
            qc.x(qr[i])
    
    qc.barrier()
    
    # Add 'b' by incrementing 'b' times
    # This is inefficient but creates depth proportional to b
    for _ in range(b):
        # Ripple-carry increment
        for i in range(n_bits):
            if i == 0:
                qc.x(qr[0])
            else:
                qc.mcx(list(qr[:i]), qr[i])
        qc.barrier()
    
    qc.measure(qr, cr)
    
    return qc


def create_multiply_by_2_circuit(n_bits: int = 4, value: int = 3) -> QuantumCircuit:
    """
    Create a circuit that computes value * 2.
    
    This is a left-shift operation - simple but reveals
    how errors propagate through bit positions.
    
    Args:
        n_bits: Width of register (needs +1 for multiplication)
        value: Value to double
        
    Returns:
        Circuit computing value * 2
    """
    qr = QuantumRegister(n_bits, 'q')
    cr = ClassicalRegister(n_bits, 'c')
    qc = QuantumCircuit(qr, cr, name=f"double_{value}")
    
    # Encode value in bits 0..n-2 (leave MSB for carry)
    for i in range(n_bits - 1):
        if (value >> i) & 1:
            qc.x(qr[i])
    
    qc.barrier()
    
    # Left shift: SWAP chain from MSB down
    # This moves each bit to the left
    for i in range(n_bits - 1, 0, -1):
        qc.swap(qr[i], qr[i-1])
    
    # Clear the LSB (shift in 0)
    # After SWAPs, bit 0 contains old bit n-1 which we need to clear
    # Actually for multiply by 2, we just need LSB = 0
    # The SWAP chain already handles this correctly for small values
    
    qc.barrier()
    qc.measure(qr, cr)
    
    return qc


def analyze_arithmetic_result(
    counts: Dict[str, int],
    expected: int,
    operation: str,
    n_bits: int,
    circuit_depth: int,
    backend: str,
    shots: int = 1024,
    job_id: Optional[str] = None,
) -> ArithmeticResult:
    """
    Analyze quantum arithmetic results.
    
    Computes accuracy and error distribution - the coherence signature.
    """
    total = sum(counts.values())
    
    # Find most likely result
    most_likely_state = max(counts, key=counts.get)
    most_likely = int(most_likely_state, 2)
    
    # Format expected as binary string
    expected_state = format(expected, f'0{n_bits}b')
    correct_count = counts.get(expected_state, 0)
    accuracy = correct_count / total
    
    # Build error distribution
    error_dist = {}
    for state, count in counts.items():
        result_val = int(state, 2)
        if result_val != expected:
            error_dist[result_val] = count / total
    
    # Compute coherence score
    # Based on accuracy and error spread
    if accuracy > 0.99:
        coherence = 1.0
    elif accuracy > 0.9:
        coherence = 0.9 + (accuracy - 0.9)
    else:
        # Factor in error spread - concentrated errors = systematic, spread = decoherence
        error_entropy = 0.0
        for prob in error_dist.values():
            if prob > 0:
                error_entropy -= prob * math.log2(prob)
        max_entropy = math.log2(2**n_bits - 1) if n_bits > 1 else 1
        error_spread = error_entropy / max_entropy if max_entropy > 0 else 0
        coherence = accuracy * (1 - 0.3 * error_spread)
    
    return ArithmeticResult(
        operation=operation,
        expected=expected,
        measured=counts,
        most_likely=most_likely,
        accuracy=accuracy,
        error_distribution=error_dist,
        circuit_depth=circuit_depth,
        backend=backend,
        coherence_score=coherence,
        timestamp=datetime.now(timezone.utc).isoformat(),
        job_id=job_id,
    )


def create_counting_sequence(max_value: int = 7, n_bits: int = 3) -> List[QuantumCircuit]:
    """
    Create a sequence of circuits that count: 0, 1, 2, 3, ...
    
    Each circuit in the sequence represents one more increment.
    Error accumulation reveals coherence gradient.
    
    Args:
        max_value: Count up to this number
        n_bits: Bit width (must hold max_value)
        
    Returns:
        List of circuits [0+1, 1+1, 2+1, ...]
    """
    circuits = []
    for v in range(max_value):
        circuits.append(create_increment_circuit(n_bits, v))
    return circuits


def create_fibonacci_test(n_steps: int = 5, n_bits: int = 4) -> List[Dict[str, Any]]:
    """
    Create Fibonacci sequence test.
    
    F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2)
    
    Returns circuit specs for verifying each step.
    """
    fib = [0, 1]
    tests = []
    
    for i in range(2, n_steps + 2):
        next_fib = fib[-1] + fib[-2]
        fib.append(next_fib)
        
        if next_fib < 2**n_bits:
            tests.append({
                "step": i,
                "a": fib[-2],
                "b": fib[-3],
                "expected": next_fib,
                "circuit": create_addition_circuit(n_bits, fib[-2], fib[-3]),
            })
    
    return tests


def create_prime_check_circuit(n: int, n_bits: int = 4) -> Dict[str, Any]:
    """
    Create a circuit spec for checking if n is prime.
    
    This is a VERIFICATION circuit - we compute trial divisions
    and check remainders. On quantum hardware, errors may produce
    false positives (claim prime when not) or false negatives.
    
    Note: This is a classical algorithm on quantum hardware.
    The value is in measuring coherence, not quantum speedup.
    
    Args:
        n: Number to check
        n_bits: Bit width
        
    Returns:
        Test specification
    """
    # Classical check for reference
    is_prime = n > 1 and all(n % i != 0 for i in range(2, int(n**0.5) + 1))
    
    # For quantum verification, we'll check divisibility
    # by trial division up to sqrt(n)
    divisor_tests = []
    for d in range(2, min(int(n**0.5) + 1, n)):
        remainder = n % d
        divisor_tests.append({
            "divisor": d,
            "expected_remainder": remainder,
            "would_divide": remainder == 0,
        })
    
    return {
        "n": n,
        "is_prime": is_prime,
        "divisor_tests": divisor_tests,
        "n_bits": n_bits,
    }


# =====================================================
# COHERENCE-ADAPTIVE ROUTING (The Runtime Strategy)
# =====================================================

@dataclass
class QubitCoherenceProfile:
    """Coherence profile for a single qubit."""
    qubit_index: int
    recent_error_rate: float
    error_trend: str  # "stable", "degrading", "improving"
    role_recommendation: str  # "compute", "verify", "entropy"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "qubit": self.qubit_index,
            "error_rate": self.recent_error_rate,
            "trend": self.error_trend,
            "role": self.role_recommendation,
        }


def analyze_qubit_coherence(
    cardiogram_history: List[Dict[str, Any]],
    qubit_index: int,
) -> QubitCoherenceProfile:
    """
    Analyze coherence trend for a specific qubit.
    
    Uses cardiogram history to determine:
    - Current error rate
    - Error trend (getting better/worse)
    - Recommended role in computation
    """
    if not cardiogram_history:
        return QubitCoherenceProfile(
            qubit_index=qubit_index,
            recent_error_rate=0.0,
            error_trend="unknown",
            role_recommendation="compute",
        )
    
    # Extract error rates for this qubit
    errors = []
    for card in cardiogram_history:
        qubit_errors = card.get("qubit_errors", [])
        if len(qubit_errors) > qubit_index:
            errors.append(qubit_errors[qubit_index])
    
    if not errors:
        return QubitCoherenceProfile(
            qubit_index=qubit_index,
            recent_error_rate=0.0,
            error_trend="unknown",
            role_recommendation="compute",
        )
    
    recent = errors[-1]
    
    # Trend analysis
    if len(errors) >= 3:
        recent_avg = sum(errors[-3:]) / 3
        older_avg = sum(errors[:-3]) / max(len(errors) - 3, 1) if len(errors) > 3 else recent_avg
        if recent_avg < older_avg * 0.9:
            trend = "improving"
        elif recent_avg > older_avg * 1.1:
            trend = "degrading"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"
    
    # Role recommendation
    if recent < 0.01:  # <1% error
        role = "compute"  # Trust for critical calculations
    elif recent < 0.05:  # <5% error
        role = "verify"  # Use as independent check
    else:
        role = "entropy"  # Use for randomness source
    
    return QubitCoherenceProfile(
        qubit_index=qubit_index,
        recent_error_rate=recent,
        error_trend=trend,
        role_recommendation=role,
    )


def create_coherence_map(
    cardiogram_history: List[Dict[str, Any]],
    num_qubits: int = 5,
) -> Dict[str, Any]:
    """
    Create a full coherence map for runtime routing decisions.
    
    Returns qubit assignments:
    - compute_qubits: Low error, use for arithmetic
    - verify_qubits: Medium error, use for checks
    - entropy_qubits: High error, use for randomness
    """
    profiles = []
    for q in range(num_qubits):
        profiles.append(analyze_qubit_coherence(cardiogram_history, q))
    
    # Sort by error rate
    compute = [p for p in profiles if p.role_recommendation == "compute"]
    verify = [p for p in profiles if p.role_recommendation == "verify"]
    entropy = [p for p in profiles if p.role_recommendation == "entropy"]
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "num_qubits": num_qubits,
        "profiles": [p.to_dict() for p in profiles],
        "routing": {
            "compute_qubits": [p.qubit_index for p in compute],
            "verify_qubits": [p.qubit_index for p in verify],
            "entropy_qubits": [p.qubit_index for p in entropy],
        },
        "summary": {
            "best_qubit": min(profiles, key=lambda p: p.recent_error_rate).qubit_index,
            "worst_qubit": max(profiles, key=lambda p: p.recent_error_rate).qubit_index,
            "mean_error": sum(p.recent_error_rate for p in profiles) / len(profiles),
        },
    }
