# IBM Quantum Interface Architecture

## The Complete Stack

Understanding what we control and what we don't.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        INTERFACE ARCHITECTURE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  LAYER 0: YOUR CODE                                                          │
│  ════════════════════════════════════════════════════════════════════════   │
│  │ Language: Python 3.10+                                                   │
│  │ Libraries: qiskit, qiskit-ibm-runtime                                   │
│  │ Control: FULL - You write the circuits and parameters                   │
│  │                                                                          │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  │  from qiskit import QuantumCircuit                               │   │
│  │  │  from qiskit_ibm_runtime import SamplerV2, QiskitRuntimeService │   │
│  │  │                                                                  │   │
│  │  │  circuit = QuantumCircuit(5)                                    │   │
│  │  │  circuit.h(0)                                                   │   │
│  │  │  circuit.cx(0, 1)                                               │   │
│  │  │  circuit.measure_all()                                          │   │
│  │  └─────────────────────────────────────────────────────────────────┘   │
│  └──────────────────────────────────────────────────────────────────────   │
│                              │                                               │
│                              ▼                                               │
│  LAYER 1: QISKIT RUNTIME SDK                                                │
│  ════════════════════════════════════════════════════════════════════════   │
│  │ What it does:                                                            │
│  │   • Validates circuit syntax                                            │
│  │   • Transpiles to target backend's native gates                         │
│  │   • Optimizes circuit depth (configurable 0-3)                          │
│  │   • Manages job submission and retrieval                                │
│  │                                                                          │
│  │ Control: PARTIAL - You set optimization_level, but IBM decides mapping │
│  │                                                                          │
│  │ Key Classes:                                                             │
│  │   • QiskitRuntimeService - Authentication and backend discovery        │
│  │   • SamplerV2 - Execute circuits, get quasi-probabilities              │
│  │   • EstimatorV2 - Compute expectation values of observables            │
│  │   • Session - Group multiple jobs for efficiency                        │
│  └──────────────────────────────────────────────────────────────────────   │
│                              │                                               │
│                              │ HTTPS REST API                                │
│                              │ Endpoint: api.quantum-computing.ibm.com      │
│                              ▼                                               │
│  LAYER 2: IBM CLOUD SERVICES                                                │
│  ════════════════════════════════════════════════════════════════════════   │
│  │ What it does:                                                            │
│  │   • IAM Authentication (API key → Bearer token)                         │
│  │   • Job queuing and scheduling                                          │
│  │   • Usage metering (your 10 minutes)                                    │
│  │   • Result storage and retrieval                                        │
│  │                                                                          │
│  │ Control: NONE - Black box queue management                              │
│  │                                                                          │
│  │ Account Details:                                                         │
│  │   • Account ID: 0eb4566b0a4640a3a59769e5d10a25d3                        │
│  │   • Instance CRN: crn:v1:bluemix:public:quantum-computing:us-east:...  │
│  │   • Service: Qiskit Runtime (open-instance)                             │
│  └──────────────────────────────────────────────────────────────────────   │
│                              │                                               │
│                              │ Internal Protocol (proprietary)              │
│                              ▼                                               │
│  LAYER 3: QUANTUM CONTROL SYSTEM                                            │
│  ════════════════════════════════════════════════════════════════════════   │
│  │ What it does:                                                            │
│  │   • Translates gates to microwave pulse sequences                       │
│  │   • Calibrates qubit frequencies (daily)                                │
│  │   • Applies error correction/mitigation                                 │
│  │   • Manages cryogenic systems                                           │
│  │                                                                          │
│  │ Control: ZERO - Completely opaque                                       │
│  │                                                                          │
│  │ Technologies involved:                                                   │
│  │   • Arbitrary Waveform Generators (AWG)                                 │
│  │   • Microwave electronics                                               │
│  │   • FPGA-based readout systems                                          │
│  │   • Classical feedback loops                                            │
│  └──────────────────────────────────────────────────────────────────────   │
│                              │                                               │
│                              │ Physical (microwave pulses at ~5 GHz)        │
│                              ▼                                               │
│  LAYER 4: QUANTUM PROCESSING UNIT (QPU)                                     │
│  ════════════════════════════════════════════════════════════════════════   │
│  │ What it is:                                                              │
│  │   • Superconducting transmon qubits                                     │
│  │   • Operating temperature: 15 millikelvin                               │
│  │   • Coherence time (T2): ~100-300 microseconds                          │
│  │   • Gate time: ~20-50 nanoseconds (single), ~300-500ns (two-qubit)     │
│  │                                                                          │
│  │ Control: ZERO - This is physics                                         │
│  │                                                                          │
│  │ What we're actually touching:                                           │
│  │   • Quantum superposition states                                        │
│  │   • Entanglement between physical qubits                                │
│  │   • Probability amplitudes that collapse on measurement                 │
│  └──────────────────────────────────────────────────────────────────────   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## What We Actually Control

### Full Control
- Circuit design (gates, topology, depth)
- Number of shots (1 to 100,000)
- Backend selection
- Optimization level (0-3)
- Session management (grouping jobs)

### Partial Control
- Qubit mapping (can provide initial_layout hints)
- Error mitigation (can enable/configure)
- Dynamical decoupling (can enable)

### No Control
- Queue position
- Physical qubit calibration
- Pulse-level operations (without Qiskit Pulse)
- Internal IBM routing and scheduling
- Actual gate fidelities on any given day

---

## Data Flow

```
Your Circuit (Python)
       │
       ▼
   Transpilation
   (Your gates → Native gates: √X, RZ, CZ)
       │
       ▼
   Serialization (QASM/QPY format)
       │
       ▼
   HTTPS POST to IBM Cloud
       │
       ▼
   Queue (seconds to hours)
       │
       ▼
   QPU Execution (~microseconds to seconds)
       │
       ▼
   Measurement Results (bitstrings)
       │
       ▼
   HTTPS Response
       │
       ▼
   Your Code (counts dictionary)
```

---

## Native Gate Set (IBM Heron)

IBM Quantum processors use a restricted gate set. Your arbitrary gates are decomposed:

| Native Gate | Description | Time |
|-------------|-------------|------|
| `√X` (SX) | √NOT gate | ~20ns |
| `RZ(θ)` | Z-rotation | Virtual (0ns) |
| `CZ` | Controlled-Z | ~300-500ns |
| `Measure` | Measurement | ~500ns |
| `Reset` | Qubit reset | ~500ns |

All other gates (H, CNOT, T, etc.) are **decomposed** into these.

---

## Connection Code

### Basic Setup
```python
import os
from qiskit_ibm_runtime import QiskitRuntimeService

# One-time save (stores in ~/.qiskit/qiskit-ibm.json)
QiskitRuntimeService.save_account(
    channel="ibm_cloud",
    token=os.getenv("IBM_QUANTUM_TOKEN"),
    instance="ibm-q/open/main",
    overwrite=True
)

# Subsequent connections
service = QiskitRuntimeService()
```

### Backend Discovery
```python
# List all available backends
backends = service.backends()
for b in backends:
    print(f"{b.name}: {b.num_qubits} qubits, status={b.status().status_msg}")

# Get least busy backend with minimum qubits
backend = service.least_busy(min_num_qubits=27, operational=True)
```

### Job Execution
```python
from qiskit_ibm_runtime import SamplerV2

sampler = SamplerV2(backend)
job = sampler.run([circuit], shots=4096)

# Job is async - this returns immediately
print(f"Job ID: {job.job_id()}")

# Block until complete
result = job.result()
counts = result[0].data.meas.get_counts()
```

---

## Error Handling

```python
from qiskit_ibm_runtime.exceptions import (
    IBMNotAuthorizedError,
    IBMRuntimeError,
    RuntimeJobFailureError
)

try:
    job = sampler.run([circuit])
    result = job.result()
except IBMNotAuthorizedError:
    # Token invalid or expired
    pass
except RuntimeJobFailureError as e:
    # Job failed on backend
    print(f"Job failed: {e}")
except IBMRuntimeError as e:
    # General runtime error
    print(f"Runtime error: {e}")
```

---

## Key Insight

**We are writing instructions that traverse 4 layers of abstraction before touching quantum physics.**

The interface is designed for ease of use, not for raw access. This is both a limitation (we can't optimize at the pulse level without extra work) and a protection (IBM handles the incredibly complex calibration and error correction).

For our purposes: **Accept the abstraction, optimize at the circuit level, and extract maximum information per QPU-second.**

---

*Document created: December 2025*
*Source: Direct IBM Quantum Platform interaction and Qiskit documentation*
