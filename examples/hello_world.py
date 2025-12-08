#!/usr/bin/env python3
"""
AIOS Quantum - Hello World Example

Based on IBM Quantum Hello World tutorial:
https://quantum.cloud.ibm.com/docs/en/tutorials/hello-world

This example demonstrates:
1. Connecting to IBM Quantum
2. Creating a Bell state circuit
3. Running on a real quantum computer
4. Analyzing results
"""

import os
import sys

# Add src to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from aios_quantum import QuantumRuntime
from aios_quantum.circuits import create_bell_state, transpile_for_backend


def main():
    """Run the Hello World quantum circuit."""
    print("=" * 50)
    print("AIOS Quantum - Hello World")
    print("=" * 50)
    
    # Initialize runtime (loads IBM_QUANTUM_TOKEN from .env)
    print("\n[1] Connecting to IBM Quantum...")
    runtime = QuantumRuntime()
    
    # List available backends
    print("\n[2] Available backends:")
    backends = runtime.get_backends()
    for backend in backends[:5]:  # Show first 5
        print(f"    - {backend}")
    if len(backends) > 5:
        print(f"    ... and {len(backends) - 5} more")
    
    # Get least busy backend
    print("\n[3] Selecting least busy backend...")
    backend = runtime.get_least_busy_backend(min_qubits=2)
    print(f"    Selected: {backend.name}")
    
    # Create Bell state circuit
    print("\n[4] Creating Bell state circuit...")
    circuit = create_bell_state()
    print(circuit.draw(output="text"))
    
    # Transpile for backend
    print("\n[5] Transpiling for backend...")
    transpiled = transpile_for_backend(circuit, backend)
    print(f"    Circuit depth: {transpiled.depth()}")
    print(f"    Gate count: {transpiled.count_ops()}")
    
    # Run with Sampler
    print("\n[6] Running on quantum hardware...")
    print("    (This may take a few minutes due to queue)")
    
    sampler = runtime.create_sampler(backend)
    job = sampler.run([transpiled], shots=1024)
    
    print(f"    Job ID: {job.job_id()}")
    print("    Waiting for results...")
    
    result = job.result()
    
    # Analyze results
    print("\n[7] Results:")
    pub_result = result[0]
    counts = pub_result.data.meas.get_counts()
    
    print(f"    Counts: {counts}")
    
    # For a Bell state, we expect roughly equal |00⟩ and |11⟩
    total = sum(counts.values())
    print("\n    Probability distribution:")
    for state, count in sorted(counts.items()):
        prob = count / total * 100
        bar = "█" * int(prob / 2)
        print(f"    |{state}⟩: {prob:5.1f}% {bar}")
    
    print("\n" + "=" * 50)
    print("Hello World complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
