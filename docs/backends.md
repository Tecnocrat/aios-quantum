# IBM Quantum Available Backends

Last updated: 2025-12-09

## Production Backends

| Backend | Qubits | Status | Description |
|---------|--------|--------|-------------|
| `ibm_fez` | 156 | Operational | Heron r2 processor |
| `ibm_marrakesh` | 156 | Operational | Heron r2 processor |
| `ibm_torino` | 133 | Operational | Heron r1 processor |

## Backend Selection

The AIOS Quantum runtime automatically selects the least busy backend for optimal queue times. You can also specify a backend manually:

```python
from aios_quantum import QuantumRuntime

runtime = QuantumRuntime()

# Auto-select least busy
backend = runtime.get_least_busy_backend(min_qubits=5)

# Or specify manually
backend = runtime.set_backend("ibm_torino")
```

## Backend Characteristics

### IBM Heron Processors (r2)
- **ibm_fez** and **ibm_marrakesh**
- 156 qubits
- Latest generation hardware
- Improved coherence times

### IBM Heron Processor (r1)
- **ibm_torino**
- 133 qubits
- First generation Heron
- Stable production system

## Notes

- All backends are available through the IBM Quantum Open Plan
- 10 free minutes of runtime per month
- Queue times vary based on demand
- Use local simulation for development to conserve runtime minutes
