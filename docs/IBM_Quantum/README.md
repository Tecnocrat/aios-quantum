# IBM Quantum Technical Reference

Technical documentation for integrating with IBM Quantum Platform.

## Contents

| Document | Description |
|----------|-------------|
| [INTERFACE_ARCHITECTURE.md](INTERFACE_ARCHITECTURE.md) | Complete stack: Python → Qiskit → IBM Cloud → QPU |
| [PRIMITIVES_AND_COMMANDS.md](PRIMITIVES_AND_COMMANDS.md) | SamplerV2, EstimatorV2, circuits, transpilation |
| [BACKEND_SPECIFICATIONS.md](BACKEND_SPECIFICATIONS.md) | Heron processors: 156-qubit specs, gate times, errors |
| [RUNTIME_BUDGET.md](RUNTIME_BUDGET.md) | Managing 10 min/month (heartbeat optimization) |

## Quick Reference

### Authentication

```python
from qiskit_ibm_runtime import QiskitRuntimeService

service = QiskitRuntimeService(
    channel="ibm_cloud",
    token=os.getenv("IBM_QUANTUM_TOKEN"),
    instance="ibm-q/open/main"
)
```

### Available Backends (Dec 2025)

| Backend | Qubits | Processor | Gate Error |
|---------|--------|-----------|------------|
| `ibm_fez` | 156 | Heron r2 | ~0.5% (CZ) |
| `ibm_marrakesh` | 156 | Heron r2 | ~0.5% (CZ) |
| `ibm_torino` | 133 | Heron r1 | ~0.8% (CZ) |

### Native Gate Set

| Gate | Time | Notes |
|------|------|-------|
| `√X` (SX) | ~20 ns | Single-qubit |
| `RZ(θ)` | 0 ns | Virtual (phase tracking) |
| `CZ` | ~70-300 ns | Two-qubit entangling |

All other gates (H, CNOT, T, etc.) are **decomposed** into these.

### Budget Summary

```
10 minutes/month = 600 seconds QPU time
÷ 720 hours = 0.83 seconds/hour
= One quantum heartbeat per hour, all month
```

## Documentation Standards

1. **Precise** — Include exact API signatures, error codes, timing
2. **Practical** — Every concept has runnable code
3. **Current** — Update when IBM changes their interface
4. **Discoverable** — Log unexpected behaviors and workarounds
