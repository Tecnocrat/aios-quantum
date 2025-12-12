#!/usr/bin/env python3
"""
Quantum Counting Test - How Fast Does 1+1 Break?

AINLP Provenance:
  origin: opus (architect)
  created: 2025-12-12
  purpose: Test coherence through simple arithmetic

The Question:
  1+1=2 on classical hardware. Always.
  On quantum hardware, how often does 1+1=2?
  At what circuit depth does counting fail?
  
  Error is not failure - it's DATA about the quantum substrate.
"""

import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dotenv import load_dotenv
load_dotenv()


def run_counting_test(use_real: bool = False, max_count: int = 7):
    """Run counting test: 0+1, 1+1, 2+1, ... up to max_count."""
    
    from aios_quantum.circuits.arithmetic import (
        create_increment_circuit,
        analyze_arithmetic_result,
    )
    
    if use_real:
        from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
        from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
        
        print("Connecting to IBM Quantum...")
        service = QiskitRuntimeService(
            channel="ibm_cloud",
            token=os.getenv("IBM_QUANTUM_TOKEN")
        )
        backend = service.least_busy(min_num_qubits=5)
        print(f"Backend: {backend.name}")
        sampler = SamplerV2(backend)
        pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
        backend_name = backend.name
    else:
        from qiskit.primitives import StatevectorSampler
        sampler = StatevectorSampler()
        pm = None
        backend_name = "simulator"
    
    print()
    print("=" * 60)
    print("  QUANTUM COUNTING TEST")
    print("=" * 60)
    print()
    print(f"Backend: {backend_name}")
    print(f"Testing: 0→1, 1→2, 2→3, ... up to {max_count-1}→{max_count}")
    print()
    
    n_bits = 4  # Enough for counting to 15
    results = []
    
    for value in range(max_count):
        expected = value + 1
        circuit = create_increment_circuit(n_bits, value)
        
        if pm:
            circuit = pm.run(circuit)
        
        job = sampler.run([circuit], shots=1024)
        result = job.result()
        
        # Get counts
        try:
            counts = result[0].data.c.get_counts()
        except:
            counts = result[0].data.meas.get_counts()
        
        # Analyze
        analysis = analyze_arithmetic_result(
            counts=counts,
            expected=expected,
            operation=f"{value}+1",
            n_bits=n_bits,
            circuit_depth=circuit.depth(),
            backend=backend_name,
        )
        results.append(analysis)
        
        # Display
        accuracy_bar = "█" * int(analysis.accuracy * 20)
        status = "✓" if analysis.accuracy > 0.9 else "⚠" if analysis.accuracy > 0.5 else "✗"
        
        print(f"  {value}+1={expected}: {analysis.most_likely} ({analysis.accuracy:.1%}) [{accuracy_bar:20}] {status}")
        
        if analysis.error_distribution:
            top_errors = sorted(analysis.error_distribution.items(), key=lambda x: -x[1])[:3]
            err_str = ", ".join(f"{v}:{p:.1%}" for v, p in top_errors)
            print(f"        errors: {err_str}")
    
    # Summary
    print()
    print("-" * 60)
    print("  SUMMARY")
    print("-" * 60)
    
    perfect = sum(1 for r in results if r.accuracy > 0.99)
    good = sum(1 for r in results if 0.9 <= r.accuracy <= 0.99)
    degraded = sum(1 for r in results if r.accuracy < 0.9)
    
    print(f"  Perfect (>99%): {perfect}/{len(results)}")
    print(f"  Good (90-99%):  {good}/{len(results)}")
    print(f"  Degraded (<90%): {degraded}/{len(results)}")
    print()
    print(f"  Mean accuracy: {sum(r.accuracy for r in results)/len(results):.2%}")
    print(f"  Mean coherence: {sum(r.coherence_score for r in results)/len(results):.3f}")
    
    # Save results
    os.makedirs("arithmetic_results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_path = f"arithmetic_results/counting_{timestamp}.json"
    
    with open(output_path, "w") as f:
        json.dump({
            "test": "counting",
            "backend": backend_name,
            "max_count": max_count,
            "results": [r.to_dict() for r in results],
        }, f, indent=2)
    
    print()
    print(f"  Saved: {output_path}")
    
    return results


def run_addition_test(use_real: bool = False):
    """Test basic addition: 1+1, 2+2, 1+2, etc."""
    
    from aios_quantum.circuits.arithmetic import (
        create_addition_circuit,
        analyze_arithmetic_result,
    )
    
    if use_real:
        from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
        from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
        
        print("Connecting to IBM Quantum...")
        service = QiskitRuntimeService(
            channel="ibm_cloud",
            token=os.getenv("IBM_QUANTUM_TOKEN")
        )
        backend = service.least_busy(min_num_qubits=5)
        sampler = SamplerV2(backend)
        pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
        backend_name = backend.name
    else:
        from qiskit.primitives import StatevectorSampler
        sampler = StatevectorSampler()
        pm = None
        backend_name = "simulator"
    
    print()
    print("=" * 60)
    print("  QUANTUM ADDITION TEST")
    print("=" * 60)
    print()
    print(f"Backend: {backend_name}")
    print()
    
    # Test cases with increasing circuit depth
    tests = [
        (1, 1, 2),   # 1+1=2 - simplest
        (2, 1, 3),   # 2+1=3
        (1, 2, 3),   # 1+2=3 - more depth
        (2, 2, 4),   # 2+2=4 - more depth
        (3, 2, 5),   # 3+2=5
        (3, 3, 6),   # 3+3=6 - deep
    ]
    
    n_bits = 4
    results = []
    
    for a, b, expected in tests:
        circuit = create_addition_circuit(n_bits, a, b)
        original_depth = circuit.depth()
        
        if pm:
            circuit = pm.run(circuit)
        
        job = sampler.run([circuit], shots=1024)
        result = job.result()
        
        # Addition circuit uses 'result' register
        try:
            counts = result[0].data.result.get_counts()
        except:
            try:
                counts = result[0].data.c.get_counts()
            except:
                counts = result[0].data.meas.get_counts()
        
        analysis = analyze_arithmetic_result(
            counts=counts,
            expected=expected,
            operation=f"{a}+{b}",
            n_bits=n_bits,
            circuit_depth=circuit.depth(),
            backend=backend_name,
        )
        results.append(analysis)
        
        # Display
        accuracy_bar = "█" * int(analysis.accuracy * 20)
        status = "✓" if analysis.accuracy > 0.9 else "⚠" if analysis.accuracy > 0.5 else "✗"
        
        print(f"  {a}+{b}={expected}: {analysis.most_likely} ({analysis.accuracy:.1%}) depth={original_depth} [{accuracy_bar:20}] {status}")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Quantum counting test")
    parser.add_argument("--real", action="store_true", help="Use IBM Quantum")
    parser.add_argument("--addition", action="store_true", help="Test addition instead of counting")
    parser.add_argument("--max", type=int, default=7, help="Maximum count value")
    args = parser.parse_args()
    
    if args.addition:
        run_addition_test(args.real)
    else:
        run_counting_test(args.real, args.max)
