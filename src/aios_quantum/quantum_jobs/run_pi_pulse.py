#!/usr/bin/env python
"""
PI PULSE RUNNER - Execute quantum π estimation on IBM Quantum

Usage:
    python -m aios_quantum.quantum_jobs.run_pi_pulse [--qubits N] [--backend NAME]

This script:
1. Creates a PI Pulse circuit (quantum phase estimation for π)
2. Submits to IBM Quantum hardware
3. Retrieves and analyzes results
4. Outputs π estimate, error, and coherence metrics
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Load environment
from dotenv import load_dotenv
load_dotenv()

from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from .pi_pulse import (
    create_pi_pulse_circuit,
    analyze_pi_result,
    map_to_hypersphere,
    recommend_circuit_size,
    PiPulseResult
)


def run_pi_pulse(
    precision_qubits: int = 8,
    backend_name: str = "ibm_torino",
    shots: int = 2048
) -> PiPulseResult:
    """
    Execute a PI Pulse circuit on IBM Quantum.
    
    Args:
        precision_qubits: Number of qubits for precision (3-20)
        backend_name: IBM Quantum backend name
        shots: Number of shots
        
    Returns:
        PiPulseResult with analysis
    """
    
    print("=" * 60)
    print("🥧 PI PULSE - Quantum π Estimation")
    print("=" * 60)
    print()
    
    # Time budget recommendation
    rec = recommend_circuit_size(10.0)
    print(f"📊 Recommended for 10s: {rec['precision_qubits']}q → ~{rec['theoretical_digits']} digits")
    print(f"   Using: {precision_qubits}q")
    print()
    
    # Create circuit
    print("🔧 Building circuit...")
    qc = create_pi_pulse_circuit(precision_qubits=precision_qubits)
    print(f"   Total qubits: {qc.num_qubits}")
    print(f"   Circuit depth: {qc.depth()}")
    print()
    
    # Connect to IBM Quantum
    print(f"🌐 Connecting to IBM Quantum...")
    token = os.getenv("IBM_QUANTUM_TOKEN")
    if not token:
        raise RuntimeError("IBM_QUANTUM_TOKEN not set in environment")
    
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)
    backend = service.backend(backend_name)
    
    print(f"   Backend: {backend_name}")
    print(f"   Qubits available: {backend.num_qubits}")
    print(f"   Status: {backend.status().status_msg}")
    print()
    
    # Transpile circuit for hardware
    print("🔄 Transpiling for hardware...")
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    qc_isa = pm.run(qc)
    print(f"   ISA circuit depth: {qc_isa.depth()}")
    print()
    
    # Submit job
    print("⚡ Submitting job...")
    start_time = time.time()
    
    sampler = Sampler(mode=backend)
    job = sampler.run([qc_isa], shots=shots)
    job_id = job.job_id()
    
    print(f"   Job ID: {job_id}")
    print(f"   Waiting for result...")
    
    # Wait for result
    result = job.result()
    
    end_time = time.time()
    execution_time_ms = (end_time - start_time) * 1000
    
    print(f"   ✓ Complete in {execution_time_ms/1000:.1f}s")
    print()
    
    # Extract counts from result
    # The result uses the classical register name 'result'
    pub_result = result[0]
    data = pub_result.data
    
    # Try different attribute names
    if hasattr(data, 'result'):
        counts_array = data.result
    elif hasattr(data, 'c'):
        counts_array = data.c
    else:
        # Get first available attribute
        attr_name = [a for a in dir(data) if not a.startswith('_')][0]
        counts_array = getattr(data, attr_name)
    
    # Convert BitArray to counts dictionary
    counts = counts_array.get_counts()
    
    print("📊 Raw Results:")
    print(f"   Total shots: {sum(counts.values())}")
    print(f"   Unique outcomes: {len(counts)}")
    
    # Show top 5 outcomes
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    print("   Top 5 outcomes:")
    for bitstring, count in sorted_counts[:5]:
        prob = count / sum(counts.values()) * 100
        print(f"      {bitstring}: {count} ({prob:.1f}%)")
    print()
    
    # Analyze result
    print("🔬 Analysis:")
    analysis = analyze_pi_result(
        counts=counts,
        precision_qubits=precision_qubits,
        shots=shots,
        backend=backend_name,
        execution_time_ms=execution_time_ms
    )
    
    # Update with circuit depth
    analysis.circuit_depth = qc.depth()
    analysis.source = "real"
    
    print(f"   Estimated π: {analysis.estimated_pi:.10f}")
    print(f"   Actual π:    {3.1415926535:.10f}")
    print(f"   Error:       {analysis.error:.10f}")
    print(f"   Correct digits: {analysis.correct_digits}")
    print(f"   Binary repr: {analysis.binary_representation}")
    print()
    
    print("📈 Coherence Metrics:")
    print(f"   Coherence: {analysis.coherence:.4f}")
    print(f"   Top probability: {analysis.top_probability:.4f}")
    print(f"   Distribution width: {analysis.distribution_width}")
    print()
    
    # Hypersphere mapping
    print("🌐 Hypersphere Coordinates:")
    coords = map_to_hypersphere(analysis)
    print(f"   θ (polar): {coords['theta']:.4f}")
    print(f"   φ (azimuth): {coords['phi']:.4f}")
    print(f"   Radius: {coords['radius']:.4f}")
    print(f"   Hue: {coords['hue']:.2f}")
    print(f"   Label: {coords['label']}")
    print()
    
    # Save result
    results_dir = Path("quantum_jobs/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"pi_pulse_{backend_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = results_dir / filename
    
    output = {
        **analysis.to_dict(),
        "hypersphere": coords,
    }
    
    with open(filepath, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"💾 Saved: {filepath}")
    
    return analysis


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Run PI Pulse on IBM Quantum")
    parser.add_argument(
        '--qubits', '-q',
        type=int, default=8,
        help='Precision qubits (default: 8)'
    )
    parser.add_argument(
        '--backend', '-b',
        default='ibm_torino',
        help='Backend name (default: ibm_torino)'
    )
    parser.add_argument(
        '--shots', '-s',
        type=int, default=2048,
        help='Number of shots (default: 2048)'
    )
    
    args = parser.parse_args()
    
    try:
        result = run_pi_pulse(
            precision_qubits=args.qubits,
            backend_name=args.backend,
            shots=args.shots
        )
        
        print("=" * 60)
        print(f"✅ PI PULSE COMPLETE")
        print(f"   π ≈ {result.estimated_pi:.6f}")
        print(f"   {result.correct_digits} correct decimal digits")
        print(f"   Coherence: {result.coherence:.2%}")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
