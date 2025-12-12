#!/usr/bin/env python3
"""
Quantum Cardiogram - Real Hardware Execution

AINLP Provenance:
  origin: opus (architect)
  created: 2025-12-12
  purpose: Generate hypersphere topology from quantum error data
"""

import os
import sys
import json
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dotenv import load_dotenv
load_dotenv()

from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from aios_quantum.circuits.cardiogram import (
    create_multi_qubit_cardiogram, 
    analyze_multi_qubit_result
)
from aios_quantum.supercell.hypersphere import HypersphereSurface


def main():
    print("=" * 60)
    print("  QUANTUM CARDIOGRAM - REAL HARDWARE")
    print("=" * 60)
    print()

    # Connect
    print("Connecting to IBM Quantum...")
    service = QiskitRuntimeService(
        channel="ibm_cloud", 
        token=os.getenv("IBM_QUANTUM_TOKEN")
    )
    backend = service.least_busy(min_num_qubits=5)
    print(f"Backend: {backend.name}")

    # Create circuit
    print("Creating cardiogram circuit (5 qubits, 5 flip-pairs)...")
    circuit = create_multi_qubit_cardiogram(5, 5)

    # Transpile
    print("Transpiling...")
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    transpiled = pm.run(circuit)
    print(f"Transpiled depth: {transpiled.depth()}")

    # Execute
    print("EXECUTING ON QUANTUM HARDWARE...")
    sampler = SamplerV2(backend)
    job = sampler.run([transpiled], shots=1024)
    print(f"Job ID: {job.job_id()}")
    result = job.result()

    # Get counts - handle the register name
    counts = result[0].data.c.get_counts()

    # Analyze
    print()
    print("=" * 60)
    print("  CARDIOGRAM RESULTS")
    print("=" * 60)
    
    analysis = analyze_multi_qubit_result(
        counts, 1024, 0, backend.name, 5, job.job_id()
    )

    overall_err = analysis["overall_error"]
    overall_fid = analysis["overall_fidelity"]
    print(f"Overall Error: {overall_err:.2%}")
    print(f"Overall Fidelity: {overall_fid:.2%}")
    print()
    print("Per-Qubit Error Rates (THE TOPOLOGY DATA):")
    
    for i, err in enumerate(analysis["qubit_errors"]):
        height = analysis["surface_data"]["heights"][i]
        bar = "#" * int(err * 200) if err > 0 else "."
        print(f"  Q{i}: {err:6.2%} -> height {height:+.3f} {bar}")

    # Generate surface
    print()
    print("Generating hypersphere surface vertex...")
    surface = HypersphereSurface()
    surface.add_multi_qubit_point(analysis["qubit_errors"], 0, 0.0)
    mesh = surface.to_mesh_data()

    # Save
    os.makedirs("cardiogram_results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    cardiogram_path = f"cardiogram_results/cardiogram_real_{timestamp}.json"
    with open(cardiogram_path, "w") as f:
        json.dump(analysis, f, indent=2)
        
    surface_path = f"cardiogram_results/surface_real_{timestamp}.json"
    with open(surface_path, "w") as f:
        json.dump(mesh, f, indent=2)

    print(f"Saved: {cardiogram_path}")
    print(f"Saved: {surface_path}")
    print()
    print("Quantum topology data generated.")
    print("Surface data ready for hypersphere projection.")


if __name__ == "__main__":
    main()
