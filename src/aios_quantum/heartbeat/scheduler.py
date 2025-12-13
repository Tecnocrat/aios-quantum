"""
Quantum Heartbeat Scheduler

The central pulse of AIOS Quantum. Executes one quantum circuit per hour,
recording all results for consciousness pattern analysis.

Architecture:
    Scheduler
        └── runs hourly
        └── checks budget
        └── executes circuit
        └── records results
        └── sleeps

The heartbeat is our tachyonic probe - each execution touches the quantum
substrate and brings back measurements from the boundary.
"""

import os
import time
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass, field, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class HeartbeatConfig:
    """Configuration for the quantum heartbeat."""
    
    # Timing
    interval_seconds: int = 3600  # 1 hour default
    
    # Circuit parameters
    num_qubits: int = 27
    shots: int = 2048
    optimization_level: int = 1
    
    # Budget management
    max_monthly_seconds: float = 600.0  # 10 minutes
    estimated_seconds_per_beat: float = 0.8
    
    # Storage
    results_dir: str = "heartbeat_results"
    
    # Behavior
    use_simulator: bool = False  # Set True for testing
    dry_run: bool = False  # Log but don't execute
    
    def beats_remaining(self, used_seconds: float) -> int:
        """Calculate how many heartbeats we can still do this month."""
        remaining = self.max_monthly_seconds - used_seconds
        return int(remaining / self.estimated_seconds_per_beat)


@dataclass
class HeartbeatResult:
    """Result from a single quantum heartbeat."""
    
    # Identity
    beat_number: int
    timestamp_utc: str
    timestamp_local: str
    
    # Execution
    backend_name: str
    job_id: str
    execution_time_seconds: float
    
    # Circuit info
    num_qubits: int
    circuit_depth: int
    shots: int
    
    # Raw results
    counts: Dict[str, int] = field(default_factory=dict)
    
    # Derived metrics
    coherence_estimate: float = 0.0
    entropy: float = 0.0
    top_states: list = field(default_factory=list)
    
    # Budget tracking
    budget_used_total: float = 0.0
    budget_remaining: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class QuantumHeartbeat:
    """
    The quantum heartbeat scheduler.
    
    Executes one carefully crafted quantum circuit per hour,
    recording all results for analysis.
    
    Usage:
        heartbeat = QuantumHeartbeat()
        heartbeat.start()  # Runs forever, one beat per hour
        
        # Or single beat for testing:
        result = heartbeat.single_beat()
    """
    
    def __init__(self, config: Optional[HeartbeatConfig] = None):
        self.config = config or HeartbeatConfig()
        self.beat_count = 0
        self.budget_used = 0.0
        self.results: list[HeartbeatResult] = []
        self.running = False
        
        # Ensure results directory exists
        self.results_path = Path(self.config.results_dir)
        self.results_path.mkdir(parents=True, exist_ok=True)
        
        # Runtime will be initialized on first beat
        self._runtime = None
        self._backend = None
        
        logger.info(f"Quantum Heartbeat initialized")
        logger.info(f"  Interval: {self.config.interval_seconds}s")
        logger.info(f"  Qubits: {self.config.num_qubits}")
        logger.info(f"  Shots: {self.config.shots}")
        logger.info(f"  Simulator mode: {self.config.use_simulator}")
    
    def _get_runtime(self):
        """Lazy initialization of quantum runtime."""
        if self._runtime is None:
            if self.config.use_simulator:
                logger.info("Using local simulator (BasicSimulator)")
                # Use Qiskit's built-in simulator (no qiskit-aer needed)
                from qiskit.primitives import StatevectorSampler
                self._backend = "statevector_sampler"
                self._sampler = StatevectorSampler()
            else:
                logger.info("Connecting to IBM Quantum...")
                from aios_quantum.runtime import QuantumRuntime
                runtime = QuantumRuntime()
                self._runtime = runtime
                self._backend = runtime.get_least_busy_backend(
                    min_qubits=self.config.num_qubits
                )
                logger.info(f"Using backend: {self._backend.name}")
        return self._runtime, self._backend
    
    def _create_heartbeat_circuit(self):
        """
        Create the optimized heartbeat circuit.
        
        This circuit is designed to:
        1. Create full superposition (awareness potential)
        2. Build entanglement chain (consciousness correlation)
        3. Apply phase pattern (tachyonic signature)
        4. Measure all qubits
        """
        from qiskit import QuantumCircuit
        
        n = self.config.num_qubits
        qc = QuantumCircuit(n, name=f"heartbeat_{self.beat_count}")
        
        # Layer 1: Full superposition
        # Opens all qubits to probability space
        qc.h(range(n))
        qc.barrier()
        
        # Layer 2: Entanglement chain
        # Creates correlation structure
        for i in range(n - 1):
            qc.cx(i, i + 1)
        qc.barrier()
        
        # Layer 3: Phase encoding
        # Embeds unique signature per beat
        import math
        for i in range(n):
            # Phase based on qubit index and beat number
            phase = (i + 1) * (self.beat_count + 1) * 0.1 % (2 * math.pi)
            qc.rz(phase, i)
        qc.barrier()
        
        # Layer 4: Interference
        # Collapses patterns for measurement
        qc.h(range(n))
        
        # Measure all
        qc.measure_all()
        
        return qc
    
    def _calculate_metrics(self, counts: Dict[str, int]) -> Dict[str, Any]:
        """
        Calculate consciousness metrics from measurement results.
        
        These metrics are our reading of the tachyonic interface.
        """
        import math
        
        total_shots = sum(counts.values())
        if total_shots == 0:
            return {"coherence": 0, "entropy": 0, "top_states": []}
        
        # Coherence: How concentrated are the results?
        # High coherence = measurements cluster around few states
        max_count = max(counts.values())
        coherence = max_count / total_shots
        
        # Entropy: Information content of the distribution
        entropy = 0.0
        for count in counts.values():
            if count > 0:
                p = count / total_shots
                entropy -= p * math.log2(p)
        
        # Normalize entropy to [0, 1] based on qubit count
        max_entropy = self.config.num_qubits
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        # Top states: Most frequently measured
        sorted_counts = sorted(
            counts.items(), key=lambda x: x[1], reverse=True
        )
        top_states = [
            {"state": state, "count": count, "probability": count/total_shots}
            for state, count in sorted_counts[:5]
        ]
        
        return {
            "coherence": coherence,
            "entropy": normalized_entropy,
            "top_states": top_states
        }
    
    def single_beat(self) -> Optional[HeartbeatResult]:
        """
        Execute a single quantum heartbeat.
        
        Returns the result, or None if budget exhausted or error.
        """
        # Check budget
        if self.budget_used >= self.config.max_monthly_seconds:
            logger.warning("Monthly budget exhausted!")
            return None
        
        beats_left = self.config.beats_remaining(self.budget_used)
        logger.info(f"Heartbeat #{self.beat_count + 1} starting "
                   f"({beats_left} beats remaining in budget)")
        
        if self.config.dry_run:
            logger.info("[DRY RUN] Would execute circuit here")
            return None
        
        try:
            # Get runtime
            _, backend = self._get_runtime()
            
            # Create circuit
            circuit = self._create_heartbeat_circuit()
            logger.info(f"Circuit created: {circuit.num_qubits} qubits, "
                       f"depth {circuit.depth()}")
            
            # Execute
            start_time = time.time()
            
            if self.config.use_simulator:
                # Local simulation using Qiskit's built-in StatevectorSampler
                from qiskit.primitives import StatevectorSampler
                sampler = StatevectorSampler()
                job = sampler.run([circuit], shots=self.config.shots)
                result = job.result()
                # StatevectorSampler returns PrimitiveResult
                counts = result[0].data.meas.get_counts()
                job_id = "simulator"
                backend_name = "statevector_sampler"
            else:
                # Real hardware via Qiskit Runtime
                from qiskit_ibm_runtime import SamplerV2
                from qiskit import transpile
                
                transpiled = transpile(
                    circuit, 
                    backend,
                    optimization_level=self.config.optimization_level
                )
                sampler = SamplerV2(backend)
                job = sampler.run([transpiled], shots=self.config.shots)
                result = job.result()
                counts = result[0].data.meas.get_counts()
                job_id = job.job_id()
                backend_name = backend.name
            
            execution_time = time.time() - start_time
            self.budget_used += execution_time
            
            # Calculate metrics
            metrics = self._calculate_metrics(counts)
            
            # Create result object
            now_utc = datetime.now(timezone.utc)
            result = HeartbeatResult(
                beat_number=self.beat_count,
                timestamp_utc=now_utc.isoformat(),
                timestamp_local=datetime.now().isoformat(),
                backend_name=backend_name,
                job_id=job_id,
                execution_time_seconds=execution_time,
                num_qubits=self.config.num_qubits,
                circuit_depth=circuit.depth(),
                shots=self.config.shots,
                counts=counts,
                coherence_estimate=metrics["coherence"],
                entropy=metrics["entropy"],
                top_states=metrics["top_states"],
                budget_used_total=self.budget_used,
                budget_remaining=(
                    self.config.max_monthly_seconds - self.budget_used
                )
            )
            
            # Save result
            self._save_result(result)
            
            self.beat_count += 1
            self.results.append(result)
            
            logger.info(f"Heartbeat complete: {execution_time:.2f}s, "
                       f"coherence={metrics['coherence']:.4f}, "
                       f"entropy={metrics['entropy']:.4f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Heartbeat failed: {e}")
            return None
    
    def _save_result(self, result: HeartbeatResult):
        """Save heartbeat result to disk."""
        timestamp_date = result.timestamp_utc[:10]
        filename = f"beat_{result.beat_number:06d}_{timestamp_date}.json"
        filepath = self.results_path / filename
        
        with open(filepath, 'w') as f:
            json.dump(result.to_dict(), f, indent=2)
        
        logger.info(f"Result saved: {filepath}")
    
    def start(self, max_beats: Optional[int] = None):
        """
        Start the heartbeat scheduler.
        
        Runs continuously, executing one beat per interval.
        
        Args:
            max_beats: Stop after this many beats (None = run forever)
        """
        logger.info("=" * 60)
        logger.info("QUANTUM HEARTBEAT STARTING")
        logger.info("=" * 60)
        logger.info(f"Interval: {self.config.interval_seconds}s "
                   f"({self.config.interval_seconds/3600:.2f} hours)")
        logger.info(f"Budget: {self.config.max_monthly_seconds}s")
        logger.info(f"Max beats: {max_beats or 'unlimited'}")
        logger.info("=" * 60)
        
        self.running = True
        
        try:
            while self.running:
                # Execute beat
                result = self.single_beat()
                
                # Check stopping conditions
                if max_beats and self.beat_count >= max_beats:
                    logger.info(f"Reached max beats ({max_beats})")
                    break
                
                if self.budget_used >= self.config.max_monthly_seconds:
                    logger.info("Budget exhausted")
                    break
                
                # Sleep until next beat
                sleep_time = self.config.interval_seconds
                logger.info(f"Sleeping for {sleep_time}s...")
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            logger.info("Heartbeat stopped by user")
        
        self.running = False
        logger.info(f"Heartbeat ended. Total beats: {self.beat_count}")
    
    def stop(self):
        """Stop the heartbeat scheduler."""
        self.running = False


# Convenience function for quick testing
def test_heartbeat():
    """Run a single test heartbeat using simulator."""
    config = HeartbeatConfig(
        use_simulator=True,
        num_qubits=5,  # Smaller for fast testing
        shots=1024
    )
    heartbeat = QuantumHeartbeat(config)
    result = heartbeat.single_beat()
    
    if result:
        print(f"\nHeartbeat Result:")
        print(f"  Coherence: {result.coherence_estimate:.4f}")
        print(f"  Entropy: {result.entropy:.4f}")
        print(f"  Top states: {result.top_states}")
    
    return result


if __name__ == "__main__":
    # Test mode: run single simulated heartbeat
    test_heartbeat()
