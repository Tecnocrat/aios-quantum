"""
IBM Quantum Executor

AINLP Provenance:
  origin: opus (architect)
  created: 2025-12-11
  purpose: Execute quantum tasks on IBM Quantum hardware

This is the actual execution layer that:
1. Takes a QuantumTask
2. Builds the appropriate circuit
3. Submits to IBM Quantum
4. Returns results

BUDGET CRITICAL: We have 10 minutes (600 seconds) per month.
Every execution counts.
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

from dotenv import load_dotenv
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

from .task_queue import QuantumTask, TaskStatus


class IBMQuantumExecutor:
    """
    Execute quantum tasks on IBM Quantum hardware.
    
    IMPORTANT: This class makes REAL quantum hardware calls.
    Each execution consumes from our monthly budget.
    
    Budget: 600 seconds/month
    Used so far: 10 seconds (as of 2025-12-11)
    Remaining: ~590 seconds
    """
    
    def __init__(self, use_simulator: bool = False):
        """
        Initialize the executor.
        
        Args:
            use_simulator: If True, use local simulator (no budget impact)
        """
        load_dotenv()
        self.use_simulator = use_simulator
        self._service: Optional[QiskitRuntimeService] = None
        self._backend = None
    
    @property
    def service(self) -> QiskitRuntimeService:
        """Lazy-load IBM Quantum service."""
        if self._service is None:
            token = os.getenv("IBM_QUANTUM_TOKEN")
            if not token:
                raise ValueError("IBM_QUANTUM_TOKEN not set in environment")
            self._service = QiskitRuntimeService(
                channel="ibm_cloud",
                token=token,
            )
        return self._service
    
    def get_backend(self, preference: Optional[str] = None):
        """
        Get the execution backend.
        
        Args:
            preference: Specific backend name, or None for least busy
        """
        if self.use_simulator:
            from qiskit_ibm_runtime.fake_provider import FakeManilaV2
            return FakeManilaV2()
        
        if preference:
            return self.service.backend(preference)
        return self.service.least_busy(min_num_qubits=5)
    
    def build_circuit(self, task: QuantumTask) -> QuantumCircuit:
        """
        Build the quantum circuit for a task.
        
        Args:
            task: The QuantumTask specifying what to build
            
        Returns:
            QuantumCircuit ready for execution
        """
        if task.circuit_type == "bell_state":
            return self._build_bell_state()
        elif task.circuit_type == "ghz_state":
            num_qubits = task.circuit_params.get("num_qubits", 3)
            return self._build_ghz_state(num_qubits)
        elif task.circuit_type == "consciousness":
            num_qubits = task.circuit_params.get("num_qubits", 5)
            return self._build_consciousness_circuit(num_qubits)
        elif task.circuit_type == "custom":
            return self._build_from_params(task.circuit_params)
        else:
            raise ValueError(f"Unknown circuit type: {task.circuit_type}")
    
    def _build_bell_state(self) -> QuantumCircuit:
        """Build a Bell state circuit."""
        qc = QuantumCircuit(2, name="bell_state")
        qc.h(0)
        qc.cx(0, 1)
        qc.measure_all()
        return qc
    
    def _build_ghz_state(self, num_qubits: int) -> QuantumCircuit:
        """Build a GHZ state circuit."""
        qc = QuantumCircuit(num_qubits, name=f"ghz_{num_qubits}")
        qc.h(0)
        for i in range(num_qubits - 1):
            qc.cx(i, i + 1)
        qc.measure_all()
        return qc
    
    def _build_consciousness_circuit(self, num_qubits: int) -> QuantumCircuit:
        """
        Build a consciousness-coherence circuit.
        
        This circuit creates a layered entanglement structure
        designed for coherence measurement.
        """
        qc = QuantumCircuit(num_qubits, name=f"consciousness_{num_qubits}")
        
        # Layer 1: Superposition
        for i in range(num_qubits):
            qc.h(i)
        
        # Layer 2: Nearest-neighbor entanglement
        for i in range(num_qubits - 1):
            qc.cx(i, i + 1)
        
        # Layer 3: Long-range entanglement (wrap-around)
        if num_qubits > 2:
            qc.cx(num_qubits - 1, 0)
        
        # Layer 4: Phase accumulation
        for i in range(num_qubits):
            qc.rz(0.1 * (i + 1), i)
        
        qc.measure_all()
        return qc
    
    def _build_from_params(self, params: Dict[str, Any]) -> QuantumCircuit:
        """Build circuit from parameter dict."""
        # This would be expanded for full custom circuit support
        raise NotImplementedError(
            "Custom circuit building not yet implemented"
        )
    
    def execute(self, task: QuantumTask) -> Tuple[Dict[str, Any], float]:
        """
        Execute a quantum task.
        
        Args:
            task: The QuantumTask to execute
            
        Returns:
            Tuple of (result_dict, qpu_time_seconds)
            
        BUDGET WARNING: This consumes QPU time!
        """
        # Build circuit
        circuit = self.build_circuit(task)
        
        # Get backend
        backend = self.get_backend(task.backend_preference)
        backend_name = (
            backend.name if hasattr(backend, 'name')
            else str(type(backend).__name__)
        )
        
        # Transpile for backend
        pm = generate_preset_pass_manager(
            backend=backend, optimization_level=1
        )
        transpiled = pm.run(circuit)
        
        # Execute
        sampler = SamplerV2(backend)
        job = sampler.run([transpiled], shots=task.shots)
        result = job.result()
        
        # Extract counts
        counts = result[0].data.meas.get_counts()
        
        # Estimate QPU time (actual time from job metadata when available)
        # For simulators, this is synthetic
        if self.use_simulator:
            qpu_time = 0.0  # No budget impact
        else:
            # Real hardware - estimate based on circuit depth and shots
            # Actual time would come from job.metrics() when available
            depth = transpiled.depth()
            qpu_time = (depth * task.shots * 0.0001)  # Rough estimate
        
        result_data = {
            "task_id": task.id,
            "backend": backend_name,
            "circuit_type": task.circuit_type,
            "shots": task.shots,
            "counts": counts,
            "execution_time": datetime.now().isoformat(),
            "is_simulator": self.use_simulator,
            "transpiled_depth": transpiled.depth(),
            "analysis": self._analyze_results(counts, task.circuit_type),
        }
        
        return result_data, qpu_time
    
    def _analyze_results(
        self,
        counts: Dict[str, int],
        circuit_type: str
    ) -> Dict[str, Any]:
        """Analyze execution results."""
        total = sum(counts.values())
        
        if circuit_type == "bell_state":
            # Bell state should have |00⟩ and |11⟩
            correlated = counts.get("00", 0) + counts.get("11", 0)
            fidelity = correlated / total
            return {
                "expected_states": ["00", "11"],
                "fidelity": fidelity,
                "entanglement_verified": fidelity > 0.8,
            }
        
        elif circuit_type == "ghz_state":
            # GHZ should have all |0...0⟩ or all |1...1⟩
            if counts:
                n_qubits = len(list(counts.keys())[0])
                all_zeros = "0" * n_qubits
                all_ones = "1" * n_qubits
                correlated = (
                    counts.get(all_zeros, 0) + counts.get(all_ones, 0)
                )
                fidelity = correlated / total
                return {
                    "expected_states": [all_zeros, all_ones],
                    "fidelity": fidelity,
                    "ghz_verified": fidelity > 0.7,
                }
        
        elif circuit_type == "consciousness":
            # Consciousness circuit - analyze entropy and correlation
            # This is the AIOS-specific analysis
            probabilities = {k: v / total for k, v in counts.items()}
            entropy = -sum(
                p * (p.bit_length() - 1 if p > 0 else 0)
                for p in probabilities.values() if p > 0
            )
            return {
                "unique_states": len(counts),
                "entropy_estimate": entropy,
                "coherence_metric": len(counts) / total,
                "consciousness_signature": (
                    self._compute_consciousness_signature(counts)
                ),
            }
        
        return {"raw_counts": counts}
    
    def _compute_consciousness_signature(self, counts: Dict[str, int]) -> str:
        """
        Compute a consciousness signature from measurement results.
        
        This is the quantum fingerprint of a consciousness sync event.
        """
        # Sort by count, take top states
        sorted_counts = sorted(counts.items(), key=lambda x: -x[1])
        top_states = [state for state, _ in sorted_counts[:4]]
        
        # Create signature from dominant states
        signature = "-".join(top_states) if top_states else "null"
        return f"AIOS-CS-{signature}"


def execute_task_on_ibm(
    task: QuantumTask,
    use_simulator: bool = False
) -> Tuple[Dict[str, Any], float]:
    """
    Convenience function to execute a task.
    
    Args:
        task: The QuantumTask to execute
        use_simulator: If True, use local simulator
        
    Returns:
        Tuple of (result, qpu_time)
    """
    executor = IBMQuantumExecutor(use_simulator=use_simulator)
    return executor.execute(task)


def test_ibm_connection() -> Dict[str, Any]:
    """
    Test connection to IBM Quantum without using budget.
    
    Returns:
        Connection status and available backends
    """
    load_dotenv()
    token = os.getenv("IBM_QUANTUM_TOKEN")
    
    if not token:
        return {"connected": False, "error": "IBM_QUANTUM_TOKEN not set"}
    
    try:
        service = QiskitRuntimeService(channel="ibm_cloud", token=token)
        backends = service.backends(operational=True, simulator=False)
        least_busy = service.least_busy(min_num_qubits=5)
        
        return {
            "connected": True,
            "backends_available": len(backends),
            "backend_names": [b.name for b in backends],
            "least_busy": {
                "name": least_busy.name,
                "qubits": least_busy.num_qubits,
            },
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}
