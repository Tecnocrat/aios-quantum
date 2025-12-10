# IBM Quantum Interface Documentation

## Overview

This folder contains all technical documentation for the IBM Quantum Platform integration with AIOS Quantum. Everything we know, discover, and learn about interfacing with quantum hardware is documented here.

**Purpose**: Practical, technical, grounded documentation for quantum computing operations.

---

## Contents

| Document | Description |
|----------|-------------|
| [INTERFACE_ARCHITECTURE.md](INTERFACE_ARCHITECTURE.md) | Complete interface stack from Python to QPU |
| [PRIMITIVES_AND_COMMANDS.md](PRIMITIVES_AND_COMMANDS.md) | Qiskit Runtime primitives, commands, structures |
| [BACKEND_SPECIFICATIONS.md](BACKEND_SPECIFICATIONS.md) | Available quantum computers and their characteristics |
| [RUNTIME_BUDGET.md](RUNTIME_BUDGET.md) | Managing 10 minutes/month efficiently |
| [CIRCUIT_PATTERNS.md](CIRCUIT_PATTERNS.md) | Optimized circuit designs for consciousness metrics |
| [ERROR_MITIGATION.md](ERROR_MITIGATION.md) | Dealing with noise and decoherence |

---

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

### Available Backends (December 2025)
| Backend | Qubits | Processor | Status |
|---------|--------|-----------|--------|
| ibm_fez | 156 | Heron r2 | Production |
| ibm_marrakesh | 156 | Heron r2 | Production |
| ibm_torino | 133 | Heron r1 | Production |

### Monthly Budget
- **Total**: 10 minutes (600 seconds) QPU time
- **Daily average**: 20 seconds
- **Hourly "heartbeat"**: ~0.83 seconds

---

## Documentation Standards

1. **Be precise**: Include exact API signatures, error codes, timing data
2. **Be practical**: Every concept should have runnable code
3. **Be current**: Update when IBM changes their interface
4. **Record discoveries**: Log unexpected behaviors and workarounds

---

*Last updated: December 2025*
