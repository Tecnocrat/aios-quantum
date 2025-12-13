#!/usr/bin/env python
"""
Quantum Job CLI - Command-line interface for quantum job management.

Usage:
    python -m aios_quantum.quantum_jobs.cli submit [--pattern NAME] [--backends B1,B2]
    python -m aios_quantum.quantum_jobs.cli status
    python -m aios_quantum.quantum_jobs.cli collect
    python -m aios_quantum.quantum_jobs.cli backends
    python -m aios_quantum.quantum_jobs.cli recent

Examples:
    # Submit consciousness probe to all fast backends
    python -m aios_quantum.quantum_jobs.cli submit --pattern consciousness
    
    # Check status of pending jobs
    python -m aios_quantum.quantum_jobs.cli status
    
    # Collect completed results
    python -m aios_quantum.quantum_jobs.cli collect
"""

import argparse
import sys
from datetime import datetime

from .manager import QuantumJobManager
from .patterns import PATTERNS, create_pattern_suite


def cmd_submit(args):
    """Submit quantum jobs."""
    manager = QuantumJobManager()
    
    # Parse backends
    if args.backends:
        backends = [b.strip() for b in args.backends.split(',')]
    else:
        backends = manager.FAST_BACKENDS
    
    print(f"=== QUANTUM JOB SUBMISSION ===")
    print(f"Pattern: {args.pattern}")
    print(f"Backends: {backends}")
    print(f"Qubits: {args.qubits}")
    print(f"Shots: {args.shots}")
    print()
    
    # Create circuit
    if args.pattern in PATTERNS:
        circuit = PATTERNS[args.pattern](num_qubits=args.qubits)
    else:
        print(f"Unknown pattern: {args.pattern}")
        print(f"Available: {list(PATTERNS.keys())}")
        return 1
    
    print(f"Circuit: {circuit.name}")
    print(f"Depth: {circuit.depth()}")
    print()
    
    # Submit
    results = manager.submit_parallel(
        circuit=circuit,
        backends=backends,
        shots=args.shots,
        experiment_type=args.pattern
    )
    
    print("Submissions:")
    for r in results:
        status = "✓" if r.submitted else "✗"
        print(f"  {status} {r.backend_name}: {r.job_id or r.error}")
    
    return 0


def cmd_status(args):
    """Check status of pending jobs."""
    manager = QuantumJobManager()
    
    print("=== PENDING JOB STATUS ===")
    print()
    
    statuses = manager.poll_pending()
    
    if not statuses:
        print("No pending jobs.")
        return 0
    
    for job_id, status in statuses.items():
        info = manager.tracker.get_job(job_id)
        backend = info.backend_name if info else "?"
        print(f"  {backend}: {status} ({job_id[:16]}...)")
    
    return 0


def cmd_collect(args):
    """Collect completed results."""
    manager = QuantumJobManager()
    
    print("=== COLLECTING COMPLETED JOBS ===")
    print()
    
    # First update statuses
    manager.poll_pending()
    
    # Collect results
    collected = manager.collect_completed()
    
    if not collected:
        print("No new results to collect.")
        return 0
    
    for job_id, data in collected:
        print(f"✓ {data['backend']}: coherence={data['metrics']['coherence']:.4f}")
        print(f"  Saved: {manager.tracker.get_job(job_id).result_file}")
    
    return 0


def cmd_backends(args):
    """Show backend status."""
    manager = QuantumJobManager()
    
    print("=== IBM QUANTUM BACKENDS ===")
    print()
    
    status = manager.get_backend_status()
    
    for name, info in status.items():
        if 'error' in info:
            print(f"  {name}: ERROR - {info['error']}")
        else:
            queue = info['pending_jobs']
            qubits = info['num_qubits']
            status_icon = "✓" if info['operational'] else "✗"
            print(f"  {status_icon} {name}: {qubits}q | Queue: {queue}")
    
    return 0


def cmd_recent(args):
    """Show recent jobs from IBM Quantum."""
    manager = QuantumJobManager()
    
    print(f"=== RECENT JOBS (last {args.limit}) ===")
    print()
    
    jobs = manager.list_recent(limit=args.limit)
    
    for j in jobs:
        print(f"  {j['backend']}: {j['status']} ({j['job_id'][:16]}...)")
    
    return 0


def cmd_suite(args):
    """Submit a full pattern suite."""
    manager = QuantumJobManager()
    
    print("=== PATTERN SUITE SUBMISSION ===")
    print()
    
    suite = create_pattern_suite(num_qubits=args.qubits)
    
    for name, circuit in suite:
        print(f"Submitting: {name} ({circuit.num_qubits}q, depth {circuit.depth()})")
        
        results = manager.submit_parallel(
            circuit=circuit,
            backends=manager.FAST_BACKENDS,
            shots=args.shots,
            experiment_type=name
        )
        
        for r in results:
            status = "✓" if r.submitted else "✗"
            print(f"  {status} {r.backend_name}: {r.job_id[:16] if r.job_id else r.error}...")
        
        print()
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Quantum Job Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Submit command
    submit_parser = subparsers.add_parser('submit', help='Submit quantum jobs')
    submit_parser.add_argument(
        '--pattern', '-p', 
        default='consciousness',
        help='Pattern name (consciousness, entanglement, walk, vqe, hypersphere)'
    )
    submit_parser.add_argument(
        '--backends', '-b',
        help='Comma-separated backend names (default: ibm_torino,ibm_fez)'
    )
    submit_parser.add_argument(
        '--qubits', '-q',
        type=int, default=10,
        help='Number of qubits (default: 10)'
    )
    submit_parser.add_argument(
        '--shots', '-s',
        type=int, default=1024,
        help='Number of shots (default: 1024)'
    )
    submit_parser.set_defaults(func=cmd_submit)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check pending jobs')
    status_parser.set_defaults(func=cmd_status)
    
    # Collect command
    collect_parser = subparsers.add_parser('collect', help='Collect completed results')
    collect_parser.set_defaults(func=cmd_collect)
    
    # Backends command
    backends_parser = subparsers.add_parser('backends', help='Show backend status')
    backends_parser.set_defaults(func=cmd_backends)
    
    # Recent command
    recent_parser = subparsers.add_parser('recent', help='Show recent jobs')
    recent_parser.add_argument(
        '--limit', '-l',
        type=int, default=10,
        help='Number of jobs to show (default: 10)'
    )
    recent_parser.set_defaults(func=cmd_recent)
    
    # Suite command
    suite_parser = subparsers.add_parser('suite', help='Submit full pattern suite')
    suite_parser.add_argument(
        '--qubits', '-q',
        type=int, default=10,
        help='Number of qubits (default: 10)'
    )
    suite_parser.add_argument(
        '--shots', '-s',
        type=int, default=1024,
        help='Number of shots (default: 1024)'
    )
    suite_parser.set_defaults(func=cmd_suite)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
