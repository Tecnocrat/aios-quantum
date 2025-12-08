#!/usr/bin/env python3
"""
AIOS Quantum - Local Simulation Example

Run quantum circuits locally without using IBM Quantum resources.
Perfect for development and testing.
"""

import os
import sys

# Add src to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from qiskit_ibm_runtime import SamplerV2

from aios_quantum import QuantumRuntime
from aios_quantum.circuits import create_bell_state, create_ghz_state, transpile_for_backend


def main():
    """Run circuits on local simulator."""
    print("=" * 50)
    print("AIOS Quantum - Local Simulation")
    print("=" * 50)
    
    # Get local simulator (no IBM token needed!)
    print("\n[1] Initializing local simulator...")
    backend = QuantumRuntime.get_local_simulator()
    print(f"    Backend: {backend.name}")
    print(f"    Qubits: {backend.num_qubits}")
    
    # Create circuits
    print("\n[2] Creating quantum circuits...")
    
    bell = create_bell_state()
    print("\n    Bell State (2 qubits):")
    print(bell.draw(output="text"))
    
    ghz = create_ghz_state(3)
    print("\n    GHZ State (3 qubits):")
    print(ghz.draw(output="text"))
    
    # Transpile circuits
    print("\n[3] Transpiling circuits...")
    bell_t = transpile_for_backend(bell, backend)
    ghz_t = transpile_for_backend(ghz, backend)
    
    # Run simulations
    print("\n[4] Running simulations...")
    sampler = SamplerV2(backend)
    
    # Run both circuits
    job = sampler.run([bell_t, ghz_t], shots=1000)
    result = job.result()
    
    # Analyze Bell state
    print("\n[5] Bell State Results:")
    bell_counts = result[0].data.meas.get_counts()
    total = sum(bell_counts.values())
    for state, count in sorted(bell_counts.items()):
        prob = count / total * 100
        bar = "█" * int(prob / 2)
        print(f"    |{state}⟩: {prob:5.1f}% {bar}")
    
    # Analyze GHZ state
    print("\n[6] GHZ State Results:")
    ghz_counts = result[1].data.meas.get_counts()
    total = sum(ghz_counts.values())
    for state, count in sorted(ghz_counts.items()):
        prob = count / total * 100
        bar = "█" * int(prob / 2)
        print(f"    |{state}⟩: {prob:5.1f}% {bar}")
    
    print("\n" + "=" * 50)
    print("Local simulation complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
