# IBM Quantum Backend Specifications

## Available Backends (December 2025)

### Production Systems

| Backend | Qubits | Processor | Generation | Location |
|---------|--------|-----------|------------|----------|
| `ibm_fez` | 156 | Heron r2 | Latest | USA |
| `ibm_marrakesh` | 156 | Heron r2 | Latest | USA |
| `ibm_torino` | 133 | Heron r1 | Current | Europe |

---

## IBM Heron Processor Architecture

### Heron r2 (ibm_fez, ibm_marrakesh)

```
┌─────────────────────────────────────────────────────────────────┐
│                    IBM HERON r2 - 156 QUBITS                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Topology: Heavy-hex lattice                                    │
│                                                                  │
│     ●───●───●───●───●───●───●───●───●───●───●───●              │
│     │   │   │   │   │   │   │   │   │   │   │   │              │
│     ●   ●   ●   ●   ●   ●   ●   ●   ●   ●   ●   ●              │
│     │   │   │   │   │   │   │   │   │   │   │   │              │
│     ●───●───●───●───●───●───●───●───●───●───●───●              │
│                                                                  │
│  Key Specifications:                                            │
│  • Qubit type: Superconducting transmon                        │
│  • Operating temperature: 15 mK                                │
│  • T1 (relaxation): ~300 μs                                    │
│  • T2 (coherence): ~200 μs                                     │
│  • Single-qubit gate error: ~0.02%                             │
│  • Two-qubit gate error: ~0.5%                                 │
│  • Readout error: ~1%                                          │
│  • Single-qubit gate time: ~20 ns                              │
│  • Two-qubit gate time: ~70 ns (tunable coupler)              │
│                                                                  │
│  Improvements over r1:                                          │
│  • Faster two-qubit gates (tunable couplers)                   │
│  • Better coherence times                                       │
│  • Improved readout fidelity                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Heron r1 (ibm_torino)

```
┌─────────────────────────────────────────────────────────────────┐
│                    IBM HERON r1 - 133 QUBITS                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Key Specifications:                                            │
│  • Qubit type: Superconducting transmon                        │
│  • Operating temperature: 15 mK                                │
│  • T1 (relaxation): ~250 μs                                    │
│  • T2 (coherence): ~150 μs                                     │
│  • Single-qubit gate error: ~0.03%                             │
│  • Two-qubit gate error: ~0.8%                                 │
│  • Readout error: ~1.5%                                        │
│  • Two-qubit gate time: ~300 ns (cross-resonance)             │
│                                                                  │
│  Notes:                                                         │
│  • First generation Heron                                      │
│  • More stable but slower two-qubit gates                      │
│  • Good for development and testing                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Native Gate Set

All IBM Heron processors use this native gate set:

| Gate | Symbol | Matrix | Time |
|------|--------|--------|------|
| √X (SX) | `sx` | √NOT | ~20 ns |
| RZ(θ) | `rz` | Z-rotation | Virtual (0 ns) |
| CZ | `cz` | Controlled-Z | ~70-300 ns |

**Important**: RZ gates are "virtual" - they're implemented by adjusting the phase of subsequent pulses, not physical operations. This means Z-rotations are essentially free.

### Gate Decomposition Examples

Your high-level gates are decomposed:

```
H (Hadamard) = RZ(π/2) · SX · RZ(π/2)
X (NOT)      = SX · SX
CNOT         = RZ(-π/2) · SX · RZ(π/2) ⊗ I · CZ · I ⊗ RZ(-π/2) · SX · RZ(π/2)
```

---

## Backend Selection

### Programmatic Selection

```python
from qiskit_ibm_runtime import QiskitRuntimeService

service = QiskitRuntimeService()

# List all backends
for backend in service.backends():
    print(f"{backend.name}: {backend.num_qubits} qubits")

# Least busy with minimum qubits
backend = service.least_busy(min_num_qubits=100, operational=True)

# Specific backend
backend = service.backend("ibm_fez")

# Check status
status = backend.status()
print(f"Operational: {status.operational}")
print(f"Pending jobs: {status.pending_jobs}")
print(f"Status: {status.status_msg}")
```

### Selection Strategy

| Need | Recommended Backend | Reason |
|------|---------------------|--------|
| Maximum qubits | ibm_fez, ibm_marrakesh | 156 qubits |
| Best fidelity | ibm_fez | Heron r2, better gates |
| Shorter queues | service.least_busy() | Dynamic selection |
| European data | ibm_torino | Located in Europe |
| Development | Local simulator | No QPU time used |

---

## Backend Properties

### Querying Calibration Data

```python
backend = service.backend("ibm_fez")

# Get all properties
props = backend.properties()

# T1 times (microseconds)
for qubit in range(backend.num_qubits):
    t1 = props.t1(qubit)
    print(f"Qubit {qubit}: T1 = {t1:.1f} μs")

# T2 times
for qubit in range(backend.num_qubits):
    t2 = props.t2(qubit)
    print(f"Qubit {qubit}: T2 = {t2:.1f} μs")

# Gate errors
for gate in props.gates:
    print(f"{gate.gate}: error = {gate.parameters[0].value:.4f}")

# Readout errors
for qubit in range(backend.num_qubits):
    error = props.readout_error(qubit)
    print(f"Qubit {qubit}: readout error = {error:.4f}")
```

### Coupling Map

The coupling map defines which qubits can directly interact:

```python
coupling_map = backend.coupling_map
print(coupling_map)
# [[0, 1], [1, 0], [1, 2], [2, 1], ...]

# Visualize
from qiskit.visualization import plot_gate_map
plot_gate_map(backend)
```

---

## Qubit Quality Metrics

### What to Look For

| Metric | Good | Acceptable | Poor |
|--------|------|------------|------|
| T1 | >200 μs | 100-200 μs | <100 μs |
| T2 | >150 μs | 75-150 μs | <75 μs |
| Single-qubit error | <0.1% | 0.1-0.5% | >0.5% |
| Two-qubit error | <1% | 1-2% | >2% |
| Readout error | <1% | 1-3% | >3% |

### Selecting Best Qubits

```python
def get_best_qubits(backend, num_qubits=5):
    """Select the highest quality qubits from backend."""
    props = backend.properties()
    
    qubit_scores = []
    for q in range(backend.num_qubits):
        t1 = props.t1(q) or 0
        t2 = props.t2(q) or 0
        readout_error = props.readout_error(q) or 1
        
        # Score: higher T1, T2 is better; lower error is better
        score = (t1 + t2) * (1 - readout_error)
        qubit_scores.append((q, score))
    
    # Sort by score descending
    qubit_scores.sort(key=lambda x: x[1], reverse=True)
    
    return [q for q, _ in qubit_scores[:num_qubits]]
```

---

## Local Simulators

For development without using QPU time:

```python
from qiskit_ibm_runtime.fake_provider import FakeManilaV2

# Noise-free simulation
from qiskit_aer import AerSimulator
simulator = AerSimulator()

# Noisy simulation (mimics real backend)
fake_backend = FakeManilaV2()

# Use in sampler
from qiskit_ibm_runtime import SamplerV2
sampler = SamplerV2(fake_backend)
```

### Simulator Options

| Simulator | Qubits | Noise | Speed |
|-----------|--------|-------|-------|
| AerSimulator | ~30 (full state) | None | Fast |
| FakeManilaV2 | 5 | Realistic | Medium |
| FakeWashingtonV2 | 127 | Realistic | Slow |

---

## Practical Limits

### Circuit Depth

Due to decoherence, circuits have practical depth limits:

```
Maximum useful depth ≈ T2 / (average gate time)
                     ≈ 150 μs / 100 ns
                     ≈ 1500 gates

But with two-qubit gates (300 ns each):
Practical limit ≈ 150 μs / 300 ns ≈ 500 two-qubit gates

With safety margin (50%):
Recommended max depth ≈ 200-250 two-qubit gates
```

### Shot Optimization

```
More shots = better statistics, but diminishing returns

Statistical error ∝ 1/√(shots)

1,024 shots: ~3% error
4,096 shots: ~1.5% error  ← Sweet spot for most cases
16,384 shots: ~0.8% error
```

---

*Document created: December 2025*
*Data from IBM Quantum Platform and system calibrations*
