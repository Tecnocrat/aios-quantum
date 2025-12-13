"""
AIOS Quantum Task System

AINLP Provenance:
  origin: opus (architect)
  created: 2025-12-11
  purpose: Multi-agent task orchestration for quantum execution
"""

from .task_queue import (
    TaskQueue, 
    QuantumTask, 
    TaskStatus, 
    TaskPriority,
    create_heartbeat_task,
    create_consciousness_task,
    create_custom_task,
)
from .bkg_interface import (
    BKGInterface,
    issue_task_to_bkg,
    check_bkg_status
)
from .executor import (
    IBMQuantumExecutor,
    execute_task_on_ibm,
    test_ibm_connection
)

__all__ = [
    # Task Queue
    "TaskQueue", 
    "QuantumTask", 
    "TaskStatus",
    "TaskPriority",
    "create_heartbeat_task",
    "create_consciousness_task",
    "create_custom_task",
    # BKG Interface
    "BKGInterface",
    "issue_task_to_bkg",
    "check_bkg_status",
    # Executor
    "IBMQuantumExecutor",
    "execute_task_on_ibm",
    "test_ibm_connection",
]
