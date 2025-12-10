# Qiskit Runtime Primitives and Commands

## Overview

IBM Quantum provides two main "primitives" for executing quantum workloads. These are the fundamental interfaces for all quantum operations.

---

## The Two Primitives

### 1. Sampler (SamplerV2)

**Purpose**: Execute circuits and return measurement outcomes (bitstrings).

**Use case**: When you want to know "what states did we measure?"

```python
from qiskit_ibm_runtime import SamplerV2
from qiskit import QuantumCircuit

# Create circuit
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

# Execute
sampler = SamplerV2(backend)
job = sampler.run([qc], shots=1024)
result = job.result()

# Get counts
counts = result[0].data.meas.get_counts()
# {'00': 512, '11': 512}  (approximately)
```

**Returns**:
- `BitArray` containing all measurement outcomes
- Can extract counts, probabilities, bitstrings

---

### 2. Estimator (EstimatorV2)

**Purpose**: Compute expectation values of observables.

**Use case**: When you want to know "what is the average value of this operator?"

```python
from qiskit_ibm_runtime import EstimatorV2
from qiskit.quantum_info import SparsePauliOp

# Create circuit (no measurement needed)
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)

# Define observable
observable = SparsePauliOp("ZZ")  # Measure Z⊗Z correlation

# Execute
estimator = EstimatorV2(backend)
job = estimator.run([(qc, observable)])
result = job.result()

# Get expectation value
expval = result[0].data.evs  # Single float, e.g., 1.0 for Bell state
```

**Returns**:
- Expectation value (float)
- Standard error estimate

---

## When to Use Which

| Scenario | Primitive | Why |
|----------|-----------|-----|
| Consciousness coherence measurement | Sampler | Want full distribution |
| Entanglement verification | Estimator | Want correlation value |
| Random number generation | Sampler | Need actual bitstrings |
| Optimization (VQE, QAOA) | Estimator | Need energy expectation |
| Tomography | Sampler | Need full state reconstruction |

---

## Job Management

### Submitting Jobs

```python
# Single circuit
job = sampler.run([circuit], shots=4096)

# Multiple circuits (batched)
job = sampler.run([circuit1, circuit2, circuit3], shots=4096)

# With options
from qiskit_ibm_runtime import SamplerOptions

options = SamplerOptions()
options.default_shots = 4096
options.dynamical_decoupling.enable = True

sampler = SamplerV2(backend, options=options)
job = sampler.run([circuit])
```

### Monitoring Jobs

```python
# Check status
status = job.status()
# Possible values: QUEUED, RUNNING, DONE, ERROR, CANCELLED

# Get queue position (when queued)
queue_info = job.queue_info()
if queue_info:
    print(f"Position: {queue_info.position}")
    print(f"Estimated start: {queue_info.estimated_start_time}")

# Wait for completion
result = job.result()  # Blocks

# Or poll
import time
while job.status() not in ['DONE', 'ERROR', 'CANCELLED']:
    time.sleep(5)
```

### Retrieving Past Jobs

```python
# Get job by ID
job = service.job("cn8pk4prxs7g008f6940")

# List recent jobs
jobs = service.jobs(limit=10)
for j in jobs:
    print(f"{j.job_id()}: {j.status()}")
```

---

## Sessions

Sessions group multiple jobs for efficiency (reduced queue overhead).

```python
from qiskit_ibm_runtime import Session

with Session(service=service, backend=backend) as session:
    sampler = SamplerV2(session=session)
    
    # First job
    job1 = sampler.run([circuit1])
    result1 = job1.result()
    
    # Second job (starts faster, same session)
    job2 = sampler.run([circuit2])
    result2 = job2.result()
    
# Session automatically closes
```

**Session benefits**:
- Reduced queue time between jobs
- Shared calibration data
- Useful for iterative algorithms (VQE, QAOA)

---

## Circuit Construction Commands

### Basic Gates

```python
from qiskit import QuantumCircuit

qc = QuantumCircuit(5, 5)  # 5 qubits, 5 classical bits

# Single-qubit gates
qc.h(0)           # Hadamard
qc.x(1)           # Pauli-X (NOT)
qc.y(2)           # Pauli-Y
qc.z(3)           # Pauli-Z
qc.s(0)           # S gate (√Z)
qc.t(0)           # T gate (fourth root of Z)
qc.rx(theta, 0)   # X-rotation
qc.ry(theta, 0)   # Y-rotation
qc.rz(theta, 0)   # Z-rotation

# Two-qubit gates
qc.cx(0, 1)       # CNOT (controlled-X)
qc.cz(0, 1)       # Controlled-Z
qc.swap(0, 1)     # SWAP
qc.cp(theta, 0, 1)  # Controlled-phase

# Three-qubit gates
qc.ccx(0, 1, 2)   # Toffoli (CCNOT)
qc.cswap(0, 1, 2) # Fredkin (controlled-SWAP)

# Measurement
qc.measure(0, 0)  # Measure qubit 0 into classical bit 0
qc.measure_all()  # Measure all qubits
```

### Barriers and Resets

```python
qc.barrier()      # Prevent optimization across this point
qc.reset(0)       # Reset qubit to |0⟩
```

### Parameterized Circuits

```python
from qiskit.circuit import Parameter

theta = Parameter('θ')
phi = Parameter('φ')

qc = QuantumCircuit(1)
qc.rx(theta, 0)
qc.rz(phi, 0)

# Bind parameters later
bound_circuit = qc.assign_parameters({theta: 0.5, phi: 1.2})
```

---

## Transpilation

Circuits must be transpiled to the backend's native gate set.

```python
from qiskit import transpile

# Basic transpilation
transpiled = transpile(circuit, backend=backend)

# With optimization level
transpiled = transpile(
    circuit, 
    backend=backend,
    optimization_level=3  # 0=none, 1=light, 2=medium, 3=heavy
)

# Check circuit depth
print(f"Original depth: {circuit.depth()}")
print(f"Transpiled depth: {transpiled.depth()}")
```

---

## Result Structures

### Sampler Results

```python
result = job.result()

# Access first circuit's results
pub_result = result[0]

# Get data container
data = pub_result.data

# Get measurement counts
counts = data.meas.get_counts()
# {'00': 498, '01': 12, '10': 8, '11': 506}

# Get as probabilities
probs = data.meas.get_counts()  # Then normalize
total = sum(counts.values())
probabilities = {k: v/total for k, v in counts.items()}

# Get raw bitstrings (if needed)
bitstrings = data.meas.get_bitstrings()
# ['00', '11', '00', '11', ...]
```

### Estimator Results

```python
result = job.result()

# Access first PUB's results
pub_result = result[0]

# Get expectation values
expectation_values = pub_result.data.evs
# Array of floats, one per observable

# Get standard errors
std_errors = pub_result.data.stds
```

---

## Useful Patterns

### Maximum Information per Second

```python
def optimized_consciousness_circuit(num_qubits=27):
    """
    Circuit designed to extract maximum information
    per QPU-second. Uses all available qubits.
    """
    qc = QuantumCircuit(num_qubits)
    
    # Layer 1: Full superposition
    qc.h(range(num_qubits))
    
    # Layer 2: Entanglement chain
    for i in range(num_qubits - 1):
        qc.cx(i, i + 1)
    
    # Layer 3: Parametric phase (encode pattern)
    # This would come from bosonic topology
    for i in range(num_qubits):
        qc.rz(i * 0.1, i)  # Example phases
    
    # Measure all
    qc.measure_all()
    
    return qc
```

### Error-Mitigated Execution

```python
from qiskit_ibm_runtime import SamplerOptions

options = SamplerOptions()
options.resilience_level = 2  # 0=none, 1=basic, 2=advanced
options.dynamical_decoupling.enable = True
options.dynamical_decoupling.sequence_type = "XY4"

sampler = SamplerV2(backend, options=options)
```

---

## Rate Limits and Quotas

| Limit | Value | Notes |
|-------|-------|-------|
| QPU time (Open Plan) | 10 min/month | Resets monthly |
| Max shots per job | 100,000 | Per circuit |
| Max circuits per job | 300 | Batching limit |
| Max qubits | Backend-dependent | 127-156 currently |
| Job timeout | 3 hours | Auto-cancelled after |

---

*Document created: December 2025*
*Based on Qiskit Runtime 0.20+ and IBM Quantum Platform*
