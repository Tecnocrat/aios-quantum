"""
Job Tracker - Persistent storage for quantum job IDs and metadata.
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List, Any

logger = logging.getLogger(__name__)


@dataclass
class JobRecord:
    """Record of a submitted quantum job."""
    job_id: str
    backend_name: str
    submitted_at: str
    status: str = "QUEUED"
    
    # Circuit metadata
    circuit_name: str = ""
    num_qubits: int = 0
    shots: int = 1024
    
    # Experiment classification
    experiment_type: str = "heartbeat"
    experiment_id: str = ""
    
    # Results (filled when complete)
    completed_at: Optional[str] = None
    execution_time: Optional[float] = None
    result_file: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JobRecord':
        return cls(**data)


class JobTracker:
    """
    Persistent tracker for quantum jobs.
    
    Stores job IDs and metadata to JSON file for later retrieval.
    Enables fire-and-forget job submission with async result collection.
    """
    
    def __init__(self, tracker_file: str = "quantum_jobs/pending_jobs.json"):
        self.tracker_path = Path(tracker_file)
        self.tracker_path.parent.mkdir(parents=True, exist_ok=True)
        self._jobs: Dict[str, JobRecord] = {}
        self._load()
    
    def _load(self):
        """Load existing jobs from disk."""
        if self.tracker_path.exists():
            try:
                data = json.loads(self.tracker_path.read_text())
                self._jobs = {
                    k: JobRecord.from_dict(v) 
                    for k, v in data.get("jobs", {}).items()
                }
                logger.info(f"Loaded {len(self._jobs)} tracked jobs")
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Could not load tracker: {e}")
                self._jobs = {}
    
    def _save(self):
        """Persist jobs to disk."""
        data = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "jobs": {k: v.to_dict() for k, v in self._jobs.items()}
        }
        self.tracker_path.write_text(json.dumps(data, indent=2))
    
    def add_job(
        self,
        job_id: str,
        backend_name: str,
        circuit_name: str = "",
        num_qubits: int = 0,
        shots: int = 1024,
        experiment_type: str = "heartbeat",
        experiment_id: str = ""
    ) -> JobRecord:
        """Register a newly submitted job."""
        record = JobRecord(
            job_id=job_id,
            backend_name=backend_name,
            submitted_at=datetime.now(timezone.utc).isoformat(),
            circuit_name=circuit_name,
            num_qubits=num_qubits,
            shots=shots,
            experiment_type=experiment_type,
            experiment_id=experiment_id
        )
        self._jobs[job_id] = record
        self._save()
        logger.info(f"Tracking job {job_id} on {backend_name}")
        return record
    
    def update_status(self, job_id: str, status: str):
        """Update job status."""
        if job_id in self._jobs:
            self._jobs[job_id].status = status
            if status == "DONE":
                self._jobs[job_id].completed_at = (
                    datetime.now(timezone.utc).isoformat()
                )
            self._save()
    
    def mark_completed(
        self, 
        job_id: str, 
        execution_time: float,
        result_file: str
    ):
        """Mark job as completed with result info."""
        if job_id in self._jobs:
            job = self._jobs[job_id]
            job.status = "DONE"
            job.completed_at = datetime.now(timezone.utc).isoformat()
            job.execution_time = execution_time
            job.result_file = result_file
            self._save()
    
    def get_pending(self) -> List[JobRecord]:
        """Get all jobs that are not completed."""
        return [
            j for j in self._jobs.values() 
            if j.status not in ("DONE", "CANCELLED", "ERROR")
        ]
    
    def get_by_status(self, status: str) -> List[JobRecord]:
        """Get jobs by status."""
        return [j for j in self._jobs.values() if j.status == status]
    
    def get_job(self, job_id: str) -> Optional[JobRecord]:
        """Get a specific job record."""
        return self._jobs.get(job_id)
    
    def get_all(self) -> List[JobRecord]:
        """Get all tracked jobs."""
        return list(self._jobs.values())
    
    def remove_job(self, job_id: str):
        """Remove a job from tracking."""
        if job_id in self._jobs:
            del self._jobs[job_id]
            self._save()
    
    def cleanup_completed(self, keep_days: int = 7):
        """Remove completed jobs older than keep_days."""
        cutoff = datetime.now(timezone.utc)
        to_remove = []
        
        for job_id, job in self._jobs.items():
            if job.status == "DONE" and job.completed_at:
                completed = datetime.fromisoformat(
                    job.completed_at.replace('Z', '+00:00')
                )
                age_days = (cutoff - completed).days
                if age_days > keep_days:
                    to_remove.append(job_id)
        
        for job_id in to_remove:
            del self._jobs[job_id]
        
        if to_remove:
            self._save()
            logger.info(f"Cleaned up {len(to_remove)} old jobs")
