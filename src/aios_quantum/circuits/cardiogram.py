"""
Quantum Cardiogram Circuit - Primitive Zero

AINLP Provenance:
  origin: opus (architect)
  created: 2025-12-12
  purpose: Measure quantum error rate as topological texture data

Theory:
  - Apply identity operation (even X gates)
  - Perfect hardware returns |0⟩ 100%
  - Real hardware shows error rate
  - Error rate becomes height data for hypersphere surface
  
The error is not noise to eliminate - it is SIGNAL to record.
The quantum beat creates texture for the bosonic surface.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import json
import math

from qiskit import QuantumCircuit


@dataclass
class CardiogramPoint:
    """
    A single measurement point in the quantum cardiogram.
    
    This becomes a vertex on the hypersphere surface:
    - error_rate → height (mountain/valley)
    - timestamp → position on surface
    - entropy → texture roughness
    """
    timestamp: str
    beat_number: int
    
    # Raw measurement
    shots: int
    counts: Dict[str, int]
    
    # Derived metrics (the topology data)
    error_rate: float          # Primary: height on surface
    fidelity: float            # 1 - error_rate
    entropy: float             # Roughness/texture
    
    # Hardware context
    backend: str
    job_id: Optional[str] = None
    
    # Circuit parameters
    num_flips: int = 10        # Depth of identity test
    num_qubits: int = 1
    
    def to_vertex(self) -> Dict[str, float]:
        """
        Convert to 3D vertex data for hypersphere projection.
        
        Returns normalized values suitable for geometric mapping:
        - height: -1.0 (valley/low error) to +1.0 (mountain/high error)
        - roughness: 0.0 (smooth) to 1.0 (rough)
        """
        # Normalize error_rate (typically 0-10%) to height (-1 to +1)
        # Low error = valley (negative), high error = mountain (positive)
        height = (self.error_rate * 20) - 1.0  # 5% error = 0, 10% = +1
        height = max(-1.0, min(1.0, height))   # Clamp
        
        return {
            "height": height,
            "roughness": self.entropy,
            "fidelity": self.fidelity,
            "beat": self.beat_number,
        }


@dataclass 
class CardiogramSession:
    """
    A sequence of cardiogram points forming a surface strip.
    
    Multiple sessions tile the hypersphere surface.
    """
    session_id: str
    start_time: str
    points: List[CardiogramPoint] = field(default_factory=list)
    
    # Surface metadata
    surface_type: str = "cardiogram_strip"
    
    def add_point(self, point: CardiogramPoint) -> None:
        """Add a measurement point to the session."""
        self.points.append(point)
    
    def to_surface_data(self) -> Dict[str, Any]:
        """
        Export as surface data for 3D engine.
        
        Format designed for extrusion into topological mesh.
        """
        vertices = [p.to_vertex() for p in self.points]
        
        return {
            "type": "cardiogram_surface",
            "session_id": self.session_id,
            "vertex_count": len(vertices),
            "vertices": vertices,
            "metadata": {
                "start_time": self.start_time,
                "end_time": (
                    self.points[-1].timestamp if self.points else None
                ),
                "mean_error": (
                    sum(p.error_rate for p in self.points) / len(self.points)
                    if self.points else 0
                ),
                "error_variance": self._compute_variance(),
            }
        }
    
    def _compute_variance(self) -> float:
        """Compute variance in error rate (surface roughness metric)."""
        if len(self.points) < 2:
            return 0.0
        mean = sum(p.error_rate for p in self.points) / len(self.points)
        variance = (
            sum((p.error_rate - mean) ** 2 for p in self.points)
            / len(self.points)
        )
        return variance


def create_cardiogram_circuit(num_flips: int = 10) -> QuantumCircuit:
    """
    Create the quantum cardiogram circuit.
    
    This is Primitive Zero - the simplest meaningful quantum operation.
    
    Operation:
        |0⟩ → X → X → X → X → ... → measure
              (even number of flips)
    
    Perfect execution: 100% |0⟩
    Real execution: (100 - error_rate)% |0⟩
    
    Args:
        num_flips: Number of X gate pairs (total gates = num_flips * 2)
        
    Returns:
        QuantumCircuit configured for error measurement
    """
    qc = QuantumCircuit(1, 1, name=f"cardiogram_{num_flips}")
    
    # Apply X gate pairs - should return to |0⟩
    for _ in range(num_flips):
        qc.x(0)  # |0⟩ → |1⟩
        qc.x(0)  # |1⟩ → |0⟩
    
    # Measure - deviations from |0⟩ are errors
    qc.measure(0, 0)
    
    return qc


def analyze_cardiogram_result(
    counts: Dict[str, int],
    shots: int,
    beat_number: int,
    backend: str,
    job_id: Optional[str] = None,
    num_flips: int = 10,
) -> CardiogramPoint:
    """
    Analyze raw measurement counts into a CardiogramPoint.
    
    Args:
        counts: Measurement results {"0": n0, "1": n1}
        shots: Total number of measurements
        beat_number: Sequential beat identifier
        backend: Hardware name
        job_id: IBM job ID if applicable
        num_flips: Circuit depth parameter
        
    Returns:
        CardiogramPoint with derived topology metrics
    """
    # Extract counts (handle different key formats)
    count_0 = counts.get("0", counts.get("0x0", 0))
    count_1 = counts.get("1", counts.get("0x1", 0))
    
    # Compute metrics
    total = count_0 + count_1
    error_rate = count_1 / total if total > 0 else 0.0
    fidelity = 1.0 - error_rate
    
    # Compute entropy (Shannon entropy of distribution)
    entropy = 0.0
    for count in [count_0, count_1]:
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)
    
    # Normalize entropy to 0-1 range (max entropy for 2 outcomes is 1 bit)
    entropy_normalized = entropy  # Already 0-1 for binary
    
    return CardiogramPoint(
        timestamp=datetime.now(timezone.utc).isoformat(),
        beat_number=beat_number,
        shots=shots,
        counts=counts,
        error_rate=error_rate,
        fidelity=fidelity,
        entropy=entropy_normalized,
        backend=backend,
        job_id=job_id,
        num_flips=num_flips,
    )


def create_multi_qubit_cardiogram(
    num_qubits: int = 5,
    num_flips: int = 5
) -> QuantumCircuit:
    """
    Create a multi-qubit cardiogram for richer surface data.
    
    Each qubit provides an independent error measurement,
    creating a higher-dimensional texture map.
    
    Args:
        num_qubits: Number of parallel error channels
        num_flips: Depth per qubit
        
    Returns:
        QuantumCircuit with parallel cardiogram channels
    """
    circuit_name = f"cardiogram_{num_qubits}q_{num_flips}f"
    qc = QuantumCircuit(num_qubits, num_qubits, name=circuit_name)
    
    for q in range(num_qubits):
        for _ in range(num_flips):
            qc.x(q)
            qc.x(q)
    
    qc.measure(range(num_qubits), range(num_qubits))
    
    return qc


def analyze_multi_qubit_result(
    counts: Dict[str, int],
    shots: int,
    beat_number: int,
    backend: str,
    num_qubits: int = 5,
    job_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Analyze multi-qubit cardiogram for surface grid data.
    
    Returns per-qubit error rates plus correlation metrics.
    """
    total = sum(counts.values())
    
    # Expected: all zeros "00000"
    expected_state = "0" * num_qubits
    correct_count = counts.get(expected_state, 0)
    overall_error = 1.0 - (correct_count / total)
    
    # Per-qubit error analysis
    qubit_errors = []
    for q in range(num_qubits):
        # Count measurements where qubit q was |1⟩
        error_count = 0
        for state, count in counts.items():
            # Handle different state formats
            state_str = state.replace("0x", "")
            if len(state_str) < num_qubits:
                state_str = state_str.zfill(num_qubits)
            # Qiskit uses little-endian, so reverse
            if len(state_str) > q and state_str[-(q+1)] == "1":
                error_count += count
        qubit_errors.append(error_count / total)
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "beat_number": beat_number,
        "backend": backend,
        "job_id": job_id,
        "shots": shots,
        "num_qubits": num_qubits,
        "counts": counts,
        "overall_error": overall_error,
        "overall_fidelity": 1.0 - overall_error,
        "qubit_errors": qubit_errors,  # Per-qubit height data
        "mean_qubit_error": sum(qubit_errors) / len(qubit_errors),
        "error_variance": (
            sum(
                (e - sum(qubit_errors)/len(qubit_errors))**2
                for e in qubit_errors
            ) / len(qubit_errors)
        ),
        "surface_data": {
            "heights": [
                e * 20 - 1.0 for e in qubit_errors
            ],  # Normalized heights
            "roughness": (
                sum(
                    (e - sum(qubit_errors)/len(qubit_errors))**2
                    for e in qubit_errors
                ) / len(qubit_errors)
            ),
        }
    }
