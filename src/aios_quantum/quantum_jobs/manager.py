"""
Quantum Job Manager - Non-blocking parallel quantum execution.

Supports:
- Parallel submission to multiple backends
- Fire-and-forget with job tracking
- Async result collection
- Complex circuit patterns
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass

from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

from .tracker import JobTracker, JobRecord

logger = logging.getLogger(__name__)


@dataclass 
class SubmissionResult:
    """Result of job submission."""
    job_id: str
    backend_name: str
    status: str
    submitted: bool
    error: Optional[str] = None


class QuantumJobManager:
    """
    Non-blocking quantum job manager.
    
    Enables fire-and-forget quantum execution with persistent tracking.
    
    Usage:
        manager = QuantumJobManager()
        
        # Submit to multiple backends simultaneously
        results = manager.submit_parallel(circuit, ['ibm_torino', 'ibm_fez'])
        
        # Later: poll for completion
        completed = manager.poll_pending()
        
        # Collect results
        for job_id, data in manager.collect_completed():
            process(data)
    """
    
    # Available backends for parallel execution
    AVAILABLE_BACKENDS = ['ibm_torino', 'ibm_fez', 'ibm_marrakesh']
    
    # Recommended backends (low queue)
    FAST_BACKENDS = ['ibm_torino', 'ibm_fez']
    
    def __init__(
        self,
        tracker_file: str = "quantum_jobs/pending_jobs.json",
        results_dir: str = "quantum_jobs/results"
    ):
        self.tracker = JobTracker(tracker_file)
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        self._service: Optional[QiskitRuntimeService] = None
    
    @property
    def service(self) -> QiskitRuntimeService:
        """Lazy-load IBM Quantum service."""
        if self._service is None:
            from dotenv import load_dotenv
            load_dotenv()
            
            self._service = QiskitRuntimeService(
                channel=os.getenv('IBM_QUANTUM_CHANNEL', 'ibm_cloud'),
                token=os.getenv('IBM_QUANTUM_TOKEN'),
                instance=os.getenv('IBM_QUANTUM_INSTANCE')
            )
        return self._service
    
    def get_backend_status(self) -> Dict[str, Dict[str, Any]]:
        """Get current status of all backends."""
        status = {}
        for name in self.AVAILABLE_BACKENDS:
            try:
                backend = self.service.backend(name)
                s = backend.status()
                status[name] = {
                    'operational': s.operational,
                    'pending_jobs': s.pending_jobs,
                    'num_qubits': backend.num_qubits
                }
            except Exception as e:
                status[name] = {'error': str(e)}
        return status
    
    def submit_single(
        self,
        circuit: QuantumCircuit,
        backend_name: str,
        shots: int = 1024,
        experiment_type: str = "custom",
        experiment_id: str = ""
    ) -> SubmissionResult:
        """
        Submit a circuit to a single backend (non-blocking).
        
        Returns immediately with job ID.
        """
        try:
            backend = self.service.backend(backend_name)
            transpiled = transpile(
                circuit, 
                backend, 
                optimization_level=1
            )
            
            sampler = SamplerV2(backend)
            job = sampler.run([transpiled], shots=shots)
            job_id = job.job_id()
            
            # Track the job
            self.tracker.add_job(
                job_id=job_id,
                backend_name=backend_name,
                circuit_name=circuit.name,
                num_qubits=circuit.num_qubits,
                shots=shots,
                experiment_type=experiment_type,
                experiment_id=experiment_id
            )
            
            return SubmissionResult(
                job_id=job_id,
                backend_name=backend_name,
                status="QUEUED",
                submitted=True
            )
            
        except Exception as e:
            logger.error(f"Failed to submit to {backend_name}: {e}")
            return SubmissionResult(
                job_id="",
                backend_name=backend_name,
                status="FAILED",
                submitted=False,
                error=str(e)
            )
    
    def submit_parallel(
        self,
        circuit: QuantumCircuit,
        backends: Optional[List[str]] = None,
        shots: int = 1024,
        experiment_type: str = "parallel",
        experiment_id: str = ""
    ) -> List[SubmissionResult]:
        """
        Submit same circuit to multiple backends simultaneously.
        
        Args:
            circuit: Quantum circuit to execute
            backends: List of backend names (default: FAST_BACKENDS)
            shots: Number of shots per backend
            experiment_type: Classification for tracking
            experiment_id: Unique experiment identifier
            
        Returns:
            List of SubmissionResult for each backend
        """
        if backends is None:
            backends = self.FAST_BACKENDS
        
        if not experiment_id:
            experiment_id = datetime.now(timezone.utc).strftime(
                f"{experiment_type}_%Y%m%d_%H%M%S"
            )
        
        results = []
        for backend_name in backends:
            result = self.submit_single(
                circuit=circuit,
                backend_name=backend_name,
                shots=shots,
                experiment_type=experiment_type,
                experiment_id=experiment_id
            )
            results.append(result)
            
            if result.submitted:
                logger.info(
                    f"Submitted {circuit.name} to {backend_name}: {result.job_id}"
                )
        
        return results
    
    def poll_pending(self) -> Dict[str, str]:
        """
        Check status of all pending jobs.
        
        Returns dict mapping job_id -> status
        """
        pending = self.tracker.get_pending()
        statuses = {}
        
        for job_record in pending:
            try:
                job = self.service.job(job_record.job_id)
                status = str(job.status())
                statuses[job_record.job_id] = status
                self.tracker.update_status(job_record.job_id, status)
            except Exception as e:
                statuses[job_record.job_id] = f"ERROR: {e}"
        
        return statuses
    
    def collect_completed(self) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Collect results from all completed jobs.
        
        Returns list of (job_id, result_data) tuples.
        """
        collected = []
        done_jobs = self.tracker.get_by_status("DONE")
        
        for job_record in done_jobs:
            # Skip if already collected
            if job_record.result_file:
                continue
            
            try:
                job = self.service.job(job_record.job_id)
                result = job.result()
                
                # Extract counts
                counts = result[0].data.meas.get_counts()
                
                # Build result data
                result_data = {
                    'job_id': job_record.job_id,
                    'backend': job_record.backend_name,
                    'experiment_type': job_record.experiment_type,
                    'experiment_id': job_record.experiment_id,
                    'submitted_at': job_record.submitted_at,
                    'completed_at': datetime.now(timezone.utc).isoformat(),
                    'num_qubits': job_record.num_qubits,
                    'shots': job_record.shots,
                    'counts': counts,
                    'metrics': self._calculate_metrics(counts)
                }
                
                # Save result
                result_file = self._save_result(result_data)
                
                # Update tracker
                self.tracker.mark_completed(
                    job_id=job_record.job_id,
                    execution_time=0,  # TODO: get from job metadata
                    result_file=result_file
                )
                
                collected.append((job_record.job_id, result_data))
                
            except Exception as e:
                logger.error(
                    f"Failed to collect {job_record.job_id}: {e}"
                )
        
        return collected
    
    def _calculate_metrics(self, counts: Dict[str, int]) -> Dict[str, float]:
        """Calculate standard metrics from measurement counts."""
        import math
        
        total = sum(counts.values())
        if total == 0:
            return {'coherence': 0, 'entropy': 0}
        
        # Coherence: concentration around dominant state
        max_count = max(counts.values())
        coherence = max_count / total
        
        # Entropy: information content
        entropy = 0.0
        for count in counts.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)
        
        return {
            'coherence': coherence,
            'entropy': entropy,
            'num_states': len(counts),
            'total_shots': total
        }
    
    def _save_result(self, result_data: Dict[str, Any]) -> str:
        """Save result to JSON file."""
        job_id = result_data['job_id']
        backend = result_data['backend']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filename = f"{backend}_{timestamp}_{job_id[:12]}.json"
        filepath = self.results_dir / filename
        
        filepath.write_text(json.dumps(result_data, indent=2))
        logger.info(f"Saved result: {filepath}")
        
        return str(filepath)
    
    def get_job_info(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed info about a specific job."""
        record = self.tracker.get_job(job_id)
        if not record:
            return None
        
        info = record.to_dict()
        
        # Get live status from IBM
        try:
            job = self.service.job(job_id)
            info['live_status'] = str(job.status())
        except Exception as e:
            info['live_status'] = f"ERROR: {e}"
        
        return info
    
    def list_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent jobs from IBM Quantum."""
        jobs = self.service.jobs(limit=limit)
        return [
            {
                'job_id': j.job_id(),
                'backend': j.backend().name if j.backend() else 'N/A',
                'status': str(j.status()),
                'created': str(j.creation_date) if j.creation_date else 'N/A'
            }
            for j in jobs
        ]
