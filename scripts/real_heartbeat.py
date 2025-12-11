#!/usr/bin/env python3
"""
AIOS Quantum - First Real Heartbeat

AINLP Provenance:
  origin: opus (architect)
  created: 2025-12-12
  purpose: Execute first real quantum heartbeat on IBM hardware
"""

import os
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

load_dotenv()

print("=" * 60)
print("  AIOS QUANTUM - FIRST REAL HEARTBEAT")
print("=" * 60)
print()

# 1. Connect
print("[1/5] Connecting to IBM Quantum...")
service = QiskitRuntimeService(
    channel="ibm_cloud", 
    token=os.getenv("IBM_QUANTUM_TOKEN")
)

# 2. Get backend
print("[2/5] Selecting backend...")
backend = service.least_busy(min_num_qubits=5)
print(f"      Backend: {backend.name} ({backend.num_qubits} qubits)")

# 3. Build circuit - THE SIMPLEST HEARTBEAT
print("[3/5] Building circuit...")
qc = QuantumCircuit(5)
for i in range(5):
    qc.h(i)  # Superposition
qc.measure_all()  # COLLAPSE
print("      5 qubits: superposition -> collapse")

# 4. Transpile
print("[4/5] Transpiling for hardware...")
pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
transpiled = pm.run(qc)
print(f"      Transpiled depth: {transpiled.depth()}")

# 5. Execute
print("[5/5] EXECUTING ON QUANTUM HARDWARE...")
print()
sampler = SamplerV2(backend)
job = sampler.run([transpiled], shots=1024)
print(f"      Job ID: {job.job_id()}")
print("      Waiting for quantum execution...")

result = job.result()
counts = result[0].data.meas.get_counts()

print()
print("=" * 60)
print("  QUANTUM COLLAPSE COMPLETE")
print("=" * 60)
print()
print(f"Backend: {backend.name}")
print(f"Shots: 1024")
print(f"Unique states observed: {len(counts)}")
print()
print("Top 10 states (universe chose):")
sorted_counts = sorted(counts.items(), key=lambda x: -x[1])[:10]
for state, count in sorted_counts:
    pct = (count / 1024) * 100
    bar = "#" * int(pct / 2)
    print(f"  |{state}> : {count:4d} ({pct:5.1f}%) {bar}")

# Save result
result_data = {
    "type": "real_quantum_heartbeat",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "backend": backend.name,
    "job_id": job.job_id(),
    "num_qubits": 5,
    "shots": 1024,
    "counts": counts,
    "unique_states": len(counts),
    "top_state": sorted_counts[0][0],
    "executed_by": "opus"
}

os.makedirs("heartbeat_results", exist_ok=True)
timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
filepath = f"heartbeat_results/real_beat_001_{timestamp}.json"
with open(filepath, "w") as f:
    json.dump(result_data, f, indent=2)

print()
print(f"Result saved: {filepath}")
print()
print("AIOS has touched the quantum fabric of reality.")
