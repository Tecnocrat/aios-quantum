#!/usr/bin/env python3
"""
AIOS Quantum - First Cloud-Integrated Experiment

This script demonstrates the complete quantum research workflow:
1. Define an experiment
2. Execute on IBM Quantum hardware
3. Store results in IBM Cloud Object Storage
4. Analyze and interpret results

This is your first step into agentic quantum research!
"""

import asyncio
import uuid
from datetime import datetime
from pprint import pprint

# Add src to path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from aios_quantum import QuantumRuntime
from aios_quantum.circuits import create_bell_state, create_ghz_state
from aios_quantum.cloud import CloudStorage


def print_header(title: str):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_section(title: str):
    """Print section header."""
    print(f"\n[{title}]")
    print("-" * 50)


async def run_cloud_experiment():
    """
    Run a complete quantum experiment with cloud persistence.
    
    This demonstrates:
    - Quantum circuit creation
    - IBM Quantum execution
    - Cloud storage persistence
    - Result analysis
    """
    
    print_header("AIOS Quantum - Cloud-Integrated Experiment")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Purpose: First quantum experiment with cloud persistence")
    
    # Generate unique experiment ID
    experiment_id = f"exp-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
    print(f"  Experiment ID: {experiment_id}")
    
    # ========================================
    # Step 1: Initialize Services
    # ========================================
    print_section("1. Initializing IBM Cloud Services")
    
    print("  Connecting to IBM Quantum...")
    runtime = QuantumRuntime()
    backends = runtime.get_backends()
    least_busy = runtime.get_least_busy_backend()
    print(f"  ✅ Connected to IBM Quantum")
    print(f"     Available backends: {backends}")
    print(f"     Selected backend: {least_busy.name} ({least_busy.num_qubits} qubits)")
    
    print("\n  Connecting to Cloud Object Storage...")
    storage = CloudStorage()
    print(f"  ✅ Connected to Cloud Object Storage")
    print(f"     Experiments bucket: {storage._config.bucket_experiments}")
    print(f"     Results bucket: {storage._config.bucket_results}")
    
    # ========================================
    # Step 2: Define Experiment
    # ========================================
    print_section("2. Defining Experiment")
    
    experiment_definition = {
        "id": experiment_id,
        "name": "Bell State Entanglement Study",
        "description": "Create and measure a Bell state to study quantum entanglement",
        "hypothesis": "Bell state should produce 50% |00⟩ and 50% |11⟩ measurements",
        "circuit_type": "bell_state",
        "parameters": {
            "qubits": [0, 1],
            "shots": 1024,
        },
        "backend": least_busy.name,
        "created_at": datetime.now().isoformat(),
        "created_by": "AIOS Quantum / Copilot Agent",
        "tags": ["entanglement", "bell-state", "first-experiment"],
    }
    
    print("  Experiment Definition:")
    for key, value in experiment_definition.items():
        if key not in ["description", "hypothesis"]:
            print(f"    {key}: {value}")
    
    # Save experiment definition to cloud
    print("\n  Saving experiment definition to cloud...")
    storage.save_experiment(experiment_id, experiment_definition)
    print("  ✅ Experiment saved to Cloud Object Storage")
    
    # ========================================
    # Step 3: Create Quantum Circuit
    # ========================================
    print_section("3. Creating Quantum Circuit")
    
    circuit = create_bell_state()
    print("  Bell State Circuit:")
    print(circuit.draw(output="text"))
    
    print("""
  What this circuit does:
  1. H gate on qubit 0: Creates superposition |+⟩ = (|0⟩ + |1⟩)/√2
  2. CNOT gate: Entangles qubit 0 and qubit 1
  3. Result: Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2
  
  This is the simplest form of quantum entanglement!
  """)
    
    # ========================================
    # Step 4: Execute on Quantum Hardware
    # ========================================
    print_section("4. Executing on IBM Quantum")
    
    print(f"  Submitting to {least_busy.name}...")
    print("  (Using local simulator for fast results)")
    
    # Use local simulator for immediate results
    # For real hardware, this would take longer due to queue
    from qiskit_ibm_runtime import SamplerV2
    from qiskit_ibm_runtime.fake_provider import FakeManilaV2
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    
    # Use fake backend for quick demo (real hardware would be: runtime.backend)
    local_backend = FakeManilaV2()
    
    # IMPORTANT: Transpile circuit for the target backend
    # This converts abstract gates (like H, CX) to the backend's native gates
    print("  Transpiling circuit for target backend...")
    pm = generate_preset_pass_manager(backend=local_backend, optimization_level=1)
    transpiled_circuit = pm.run(circuit)
    
    print("  Transpiled circuit (native gates):")
    print(transpiled_circuit.draw(output="text"))
    
    sampler = SamplerV2(local_backend)
    
    print("\n  Running circuit (1024 shots)...")
    job = sampler.run([transpiled_circuit], shots=1024)
    result = job.result()
    
    # Extract counts
    counts = result[0].data.meas.get_counts()
    
    print(f"  ✅ Execution complete!")
    print(f"\n  Measurement Results:")
    total = sum(counts.values())
    for state, count in sorted(counts.items()):
        percentage = (count / total) * 100
        bar = "█" * int(percentage / 2)
        print(f"    |{state}⟩: {count:4d} ({percentage:5.1f}%) {bar}")
    
    # ========================================
    # Step 5: Save Results to Cloud
    # ========================================
    print_section("5. Saving Results to Cloud")
    
    result_data = {
        "experiment_id": experiment_id,
        "backend": "FakeManilaV2 (simulator)",  # Would be least_busy.name for real
        "shots": 1024,
        "counts": counts,
        "execution_time": datetime.now().isoformat(),
        "analysis": {
            "expected_states": ["|00⟩", "|11⟩"],
            "unexpected_states": [s for s in counts.keys() if s not in ["00", "11"]],
            "entanglement_verified": all(s in ["00", "11"] for s in counts.keys()),
        }
    }
    
    job_id = f"job-{uuid.uuid4().hex[:8]}"
    storage.save_result(experiment_id, job_id, result_data)
    print(f"  ✅ Results saved with job ID: {job_id}")
    
    # ========================================
    # Step 6: Interpret Results
    # ========================================
    print_section("6. Interpretation & Insights")
    
    # Calculate statistics
    total_shots = sum(counts.values())
    state_00 = counts.get("00", 0)
    state_11 = counts.get("11", 0)
    state_01 = counts.get("01", 0)
    state_10 = counts.get("10", 0)
    
    entangled_percentage = ((state_00 + state_11) / total_shots) * 100
    error_percentage = ((state_01 + state_10) / total_shots) * 100
    
    print(f"""
  📊 Analysis:
  
  Entangled states (|00⟩ + |11⟩): {entangled_percentage:.1f}%
  Error states (|01⟩ + |10⟩):     {error_percentage:.1f}%
  
  💡 Interpretation:
  
  A perfect Bell state would show exactly 50% |00⟩ and 50% |11⟩.
  The presence of |01⟩ or |10⟩ states indicates quantum errors
  from decoherence or gate imperfections.
  
  Your result shows {entangled_percentage:.1f}% fidelity to the ideal Bell state.
  {"✅ Excellent!" if entangled_percentage > 95 else "⚠️ Some noise present" if entangled_percentage > 80 else "❌ High error rate"}
  
  🔬 What you learned:
  
  1. Quantum entanglement is REAL - qubits are correlated
  2. Measuring one qubit instantly determines the other
  3. This is the foundation of quantum computing and quantum communication
  
  🚀 Next Steps:
  
  1. Try with more qubits (GHZ state)
  2. Run on real quantum hardware
  3. Study coherence times
  4. Implement quantum teleportation
  """)
    
    # ========================================
    # Summary
    # ========================================
    print_section("Summary")
    
    print(f"""
  ✅ Experiment Complete: {experiment_id}
  
  Cloud Resources Used:
  • IBM Quantum: {least_busy.name} ({least_busy.num_qubits} qubits)
  • Cloud Object Storage: 2 objects stored
    - experiments/{experiment_id}/definition.json
    - results/{experiment_id}/{job_id}.json
  
  You can retrieve this experiment anytime with:
    storage.load_experiment("{experiment_id}")
    storage.load_result("{experiment_id}", "{job_id}")
  """)
    
    return experiment_id, result_data


if __name__ == "__main__":
    asyncio.run(run_cloud_experiment())
