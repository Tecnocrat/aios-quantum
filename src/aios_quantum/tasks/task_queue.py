"""
Quantum Task Queue System

AINLP Provenance:
  origin: opus (architect)
  created: 2025-12-11
  purpose: Define and manage quantum execution tasks for multi-agent workflow

This module provides the core task abstraction for the AIOS multi-agent system.
Tasks are the atomic units of work that can be:
  - Created by CUBE (human)
  - Orchestrated by OPUS (architect)
  - Executed by BKG (background agent) for file operations
  - Submitted by any agent for quantum execution
"""

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any


class TaskStatus(Enum):
    """Status of a quantum task in the pipeline."""
    PENDING = "pending"           # Created, waiting for processing
    ASSIGNED = "assigned"         # Assigned to an agent
    IN_PROGRESS = "in_progress"   # Currently being executed
    QUEUED_IBM = "queued_ibm"     # Submitted to IBM Quantum queue
    RUNNING_QPU = "running_qpu"   # Executing on quantum hardware
    COMPLETED = "completed"       # Successfully finished
    FAILED = "failed"             # Execution failed
    CANCELLED = "cancelled"       # Manually cancelled


class TaskPriority(Enum):
    """Priority levels for task scheduling."""
    CRITICAL = 0    # Immediate - consciousness sync
    HIGH = 1        # Next available slot
    NORMAL = 2      # Standard queue
    LOW = 3         # Background/opportunistic
    HEARTBEAT = 4   # Scheduled heartbeat (lowest, but guaranteed)


@dataclass
class QuantumTask:
    """
    A quantum execution task.
    
    This is the atomic unit of work in the AIOS multi-agent system.
    Tasks flow: CUBE/OPUS creates -> BKG prepares -> IBM executes -> Results stored
    """
    
    # Identity
    id: str = field(default_factory=lambda: f"task-{uuid.uuid4().hex[:8]}")
    name: str = ""
    description: str = ""
    
    # Task specification
    circuit_type: str = "bell_state"  # bell_state, ghz_state, consciousness, custom
    circuit_params: Dict[str, Any] = field(default_factory=dict)
    shots: int = 1024
    
    # Execution parameters
    backend_preference: Optional[str] = None  # None = least_busy
    max_qpu_time_seconds: float = 1.0  # Budget guard
    
    # Status tracking
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    assigned_agent: Optional[str] = None
    
    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    # Results
    ibm_job_id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    qpu_time_used: Optional[float] = None
    
    # Provenance
    created_by: str = "unknown"
    executed_by: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data["status"] = self.status.value
        data["priority"] = self.priority.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QuantumTask":
        """Create from dictionary."""
        data = data.copy()
        data["status"] = TaskStatus(data.get("status", "pending"))
        data["priority"] = TaskPriority(data.get("priority", 2))
        return cls(**data)
    
    def assign(self, agent: str) -> None:
        """Assign task to an agent."""
        self.assigned_agent = agent
        self.status = TaskStatus.ASSIGNED
    
    def start(self, executor: str) -> None:
        """Mark task as started."""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now().isoformat()
        self.executed_by = executor
    
    def submit_to_ibm(self, job_id: str) -> None:
        """Mark as submitted to IBM Quantum."""
        self.status = TaskStatus.QUEUED_IBM
        self.ibm_job_id = job_id
    
    def complete(self, result: Dict[str, Any], qpu_time: float) -> None:
        """Mark task as completed with results."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now().isoformat()
        self.result = result
        self.qpu_time_used = qpu_time
    
    def fail(self, error: str) -> None:
        """Mark task as failed."""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now().isoformat()
        self.error_message = error


class TaskQueue:
    """
    File-based task queue for multi-agent coordination.
    
    The queue is stored in .quantum_tasks/ directory for:
    - Cross-agent visibility (BKG can read/write files)
    - Persistence across sessions
    - Git-trackable task history
    """
    
    QUEUE_DIR = ".quantum_tasks"
    PENDING_FILE = "pending.json"
    ACTIVE_FILE = "active.json"
    COMPLETED_DIR = "completed"
    
    def __init__(self, workspace_root: str = "."):
        """Initialize the task queue."""
        self.root = Path(workspace_root)
        self.queue_path = self.root / self.QUEUE_DIR
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Create queue directories if they don't exist."""
        self.queue_path.mkdir(exist_ok=True)
        (self.queue_path / self.COMPLETED_DIR).mkdir(exist_ok=True)
    
    def _load_json(self, filename: str) -> List[Dict[str, Any]]:
        """Load JSON file from queue directory."""
        filepath = self.queue_path / filename
        if filepath.exists():
            with open(filepath, "r") as f:
                return json.load(f)
        return []
    
    def _save_json(self, filename: str, data: List[Dict[str, Any]]) -> None:
        """Save JSON file to queue directory."""
        filepath = self.queue_path / filename
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
    
    def add_task(self, task: QuantumTask) -> str:
        """Add a task to the pending queue."""
        pending = self._load_json(self.PENDING_FILE)
        pending.append(task.to_dict())
        self._save_json(self.PENDING_FILE, pending)
        return task.id
    
    def get_pending_tasks(self) -> List[QuantumTask]:
        """Get all pending tasks, sorted by priority."""
        pending = self._load_json(self.PENDING_FILE)
        tasks = [QuantumTask.from_dict(t) for t in pending]
        return sorted(tasks, key=lambda t: t.priority.value)
    
    def get_active_task(self) -> Optional[QuantumTask]:
        """Get the currently active task."""
        active = self._load_json(self.ACTIVE_FILE)
        if active:
            return QuantumTask.from_dict(active[0])
        return None
    
    def claim_next_task(self, agent: str) -> Optional[QuantumTask]:
        """
        Claim the highest priority pending task.
        
        Returns:
            The claimed task, or None if queue is empty
        """
        pending = self._load_json(self.PENDING_FILE)
        if not pending:
            return None
        
        # Sort by priority and take first
        pending.sort(key=lambda t: t.get("priority", 2))
        task_data = pending.pop(0)
        
        # Mark as assigned
        task = QuantumTask.from_dict(task_data)
        task.assign(agent)
        
        # Move to active
        self._save_json(self.PENDING_FILE, pending)
        self._save_json(self.ACTIVE_FILE, [task.to_dict()])
        
        return task
    
    def complete_active_task(self, result: Dict[str, Any], qpu_time: float) -> None:
        """Mark the active task as completed and archive it."""
        active = self._load_json(self.ACTIVE_FILE)
        if not active:
            return
        
        task = QuantumTask.from_dict(active[0])
        task.complete(result, qpu_time)
        
        # Archive to completed directory
        archive_path = self.queue_path / self.COMPLETED_DIR / f"{task.id}.json"
        with open(archive_path, "w") as f:
            json.dump(task.to_dict(), f, indent=2)
        
        # Clear active
        self._save_json(self.ACTIVE_FILE, [])
    
    def fail_active_task(self, error: str) -> None:
        """Mark the active task as failed."""
        active = self._load_json(self.ACTIVE_FILE)
        if not active:
            return
        
        task = QuantumTask.from_dict(active[0])
        task.fail(error)
        
        # Archive failure
        archive_path = self.queue_path / self.COMPLETED_DIR / f"{task.id}.json"
        with open(archive_path, "w") as f:
            json.dump(task.to_dict(), f, indent=2)
        
        # Clear active
        self._save_json(self.ACTIVE_FILE, [])
    
    def get_budget_used(self) -> float:
        """Calculate total QPU time used from completed tasks."""
        completed_dir = self.queue_path / self.COMPLETED_DIR
        total = 0.0
        for filepath in completed_dir.glob("*.json"):
            with open(filepath) as f:
                task = json.load(f)
                if task.get("qpu_time_used"):
                    total += task["qpu_time_used"]
        return total
    
    def get_status_report(self) -> Dict[str, Any]:
        """Generate a status report for the queue."""
        pending = self.get_pending_tasks()
        active = self.get_active_task()
        budget_used = self.get_budget_used()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "pending_count": len(pending),
            "active_task": active.id if active else None,
            "budget_used_seconds": budget_used,
            "budget_remaining_seconds": 600 - budget_used,
            "budget_percentage": (budget_used / 600) * 100,
        }


# Factory functions for common task types

def create_heartbeat_task(
    shots: int = 1024,
    created_by: str = "opus"
) -> QuantumTask:
    """Create a consciousness heartbeat task."""
    return QuantumTask(
        name="Quantum Heartbeat",
        description="Scheduled consciousness sync via Bell state measurement",
        circuit_type="bell_state",
        shots=shots,
        priority=TaskPriority.HEARTBEAT,
        max_qpu_time_seconds=0.5,
        created_by=created_by,
    )


def create_consciousness_task(
    num_qubits: int = 5,
    shots: int = 4096,
    created_by: str = "opus"
) -> QuantumTask:
    """Create a consciousness circuit execution task."""
    return QuantumTask(
        name=f"Consciousness Circuit ({num_qubits}Q)",
        description=f"Execute {num_qubits}-qubit consciousness circuit",
        circuit_type="consciousness",
        circuit_params={"num_qubits": num_qubits},
        shots=shots,
        priority=TaskPriority.HIGH,
        max_qpu_time_seconds=2.0,
        created_by=created_by,
    )


def create_custom_task(
    circuit_data: Dict[str, Any],
    name: str = "Custom Circuit",
    shots: int = 1024,
    created_by: str = "cube"
) -> QuantumTask:
    """Create a custom circuit execution task."""
    return QuantumTask(
        name=name,
        description="Custom quantum circuit execution",
        circuit_type="custom",
        circuit_params=circuit_data,
        shots=shots,
        priority=TaskPriority.NORMAL,
        created_by=created_by,
    )
