"""
Quantum Job Management System

Fire-and-track architecture for non-blocking quantum execution.

Usage:
    # Submit jobs to multiple backends
    from aios_quantum.quantum_jobs import QuantumJobManager
    
    manager = QuantumJobManager()
    job_ids = manager.submit_parallel(circuit, backends=['ibm_torino', 'ibm_fez'])
    
    # Later: check status
    statuses = manager.check_all()
    
    # Retrieve completed results
    results = manager.collect_completed()
"""

from .manager import QuantumJobManager
from .tracker import JobTracker

__all__ = ['QuantumJobManager', 'JobTracker']
