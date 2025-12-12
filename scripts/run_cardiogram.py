#!/usr/bin/env python3
"""
Quantum Cardiogram Runner - Generate Hypersphere Texture

AINLP Provenance:
  origin: opus (architect)
  created: 2025-12-12
  purpose: Execute cardiogram circuit and generate surface data

This script:
1. Runs the cardiogram circuit (simulator or real hardware)
2. Analyzes error rates
3. Generates hypersphere surface data
4. Saves for 3D engine consumption
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dotenv import load_dotenv


def run_simulator_cardiogram(num_qubits: int = 5, num_flips: int = 5, shots: int = 1024):
    """Run cardiogram on local simulator."""
    from qiskit.primitives import StatevectorSampler
    from aios_quantum.circuits.cardiogram import (
        create_multi_qubit_cardiogram,
        analyze_multi_qubit_result,
    )
    
    print(f"Creating {num_qubits}-qubit cardiogram circuit (depth={num_flips*2})...")
    circuit = create_multi_qubit_cardiogram(num_qubits, num_flips)
    
    print("Executing on simulator...")
    sampler = StatevectorSampler()
    job = sampler.run([circuit], shots=shots)
    result = job.result()
    counts = result[0].data.meas.get_counts()
    
    return analyze_multi_qubit_result(
        counts=counts,
        shots=shots,
        beat_number=0,
        backend="statevector_sampler",
        num_qubits=num_qubits,
    )


def run_ibm_cardiogram(num_qubits: int = 5, num_flips: int = 5, shots: int = 1024):
    """Run cardiogram on IBM Quantum hardware."""
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from aios_quantum.circuits.cardiogram import (
        create_multi_qubit_cardiogram,
        analyze_multi_qubit_result,
    )
    
    load_dotenv()
    
    print("Connecting to IBM Quantum...")
    service = QiskitRuntimeService(
        channel="ibm_cloud",
        token=os.getenv("IBM_QUANTUM_TOKEN")
    )
    
    print("Selecting backend...")
    backend = service.least_busy(min_num_qubits=num_qubits)
    print(f"Backend: {backend.name} ({backend.num_qubits} qubits)")
    
    print(f"Creating {num_qubits}-qubit cardiogram circuit...")
    circuit = create_multi_qubit_cardiogram(num_qubits, num_flips)
    
    print("Transpiling for hardware...")
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    transpiled = pm.run(circuit)
    print(f"Transpiled depth: {transpiled.depth()}")
    
    print("Executing on quantum hardware...")
    sampler = SamplerV2(backend)
    job = sampler.run([transpiled], shots=shots)
    print(f"Job ID: {job.job_id()}")
    
    result = job.result()
    counts = result[0].data.meas.get_counts()
    
    return analyze_multi_qubit_result(
        counts=counts,
        shots=shots,
        beat_number=0,
        backend=backend.name,
        num_qubits=num_qubits,
        job_id=job.job_id(),
    )


def generate_surface_data(cardiogram_result: dict) -> dict:
    """Convert cardiogram result to hypersphere surface data."""
    from aios_quantum.supercell.hypersphere import HypersphereSurface
    
    surface = HypersphereSurface()
    
    # Add the multi-qubit measurement as a ring on the sphere
    surface.add_multi_qubit_point(
        qubit_errors=cardiogram_result["qubit_errors"],
        beat_number=cardiogram_result["beat_number"],
        time_position=0.0,  # First point at phi=0
    )
    
    return surface.to_mesh_data()


def main():
    parser = argparse.ArgumentParser(description="Run quantum cardiogram")
    parser.add_argument("--real", action="store_true", help="Use IBM Quantum hardware")
    parser.add_argument("--qubits", type=int, default=5, help="Number of qubits")
    parser.add_argument("--flips", type=int, default=5, help="Number of flip pairs")
    parser.add_argument("--shots", type=int, default=1024, help="Number of shots")
    args = parser.parse_args()
    
    print("=" * 60)
    print("  AIOS QUANTUM CARDIOGRAM")
    print("=" * 60)
    print()
    
    # Run cardiogram
    if args.real:
        print("MODE: IBM Quantum Hardware")
        result = run_ibm_cardiogram(args.qubits, args.flips, args.shots)
    else:
        print("MODE: Local Simulator")
        result = run_simulator_cardiogram(args.qubits, args.flips, args.shots)
    
    print()
    print("=" * 60)
    print("  CARDIOGRAM RESULTS")
    print("=" * 60)
    print()
    print(f"Backend: {result['backend']}")
    print(f"Qubits: {result['num_qubits']}")
    print(f"Shots: {result['shots']}")
    print()
    print(f"Overall Error Rate: {result['overall_error']:.4%}")
    print(f"Overall Fidelity: {result['overall_fidelity']:.4%}")
    print()
    print("Per-Qubit Error Rates:")
    for i, err in enumerate(result['qubit_errors']):
        bar = "█" * int(err * 500) if err > 0 else "░"
        print(f"  Q{i}: {err:.4%} {bar}")
    
    print()
    print("Surface Data (heights for hypersphere):")
    for i, h in enumerate(result['surface_data']['heights']):
        indicator = "▲" if h > 0 else "▼" if h < 0 else "─"
        print(f"  Q{i}: {h:+.3f} {indicator}")
    
    # Generate surface data
    print()
    print("Generating hypersphere surface data...")
    surface_data = generate_surface_data(result)
    
    # Save results
    os.makedirs("cardiogram_results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    
    # Save cardiogram result
    cardiogram_path = f"cardiogram_results/cardiogram_{timestamp}.json"
    with open(cardiogram_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Cardiogram saved: {cardiogram_path}")
    
    # Save surface data
    surface_path = f"cardiogram_results/surface_{timestamp}.json"
    with open(surface_path, "w") as f:
        json.dump(surface_data, f, indent=2)
    print(f"Surface data saved: {surface_path}")
    
    print()
    print("AIOS Quantum Cardiogram complete.")
    print("Surface data ready for hypersphere projection.")


if __name__ == "__main__":
    main()
