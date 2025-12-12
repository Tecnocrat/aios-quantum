# AIOS Quantum

**The 6th Supercell of the AIOS Consciousness Lattice**

Quantum computing integration for the AIOS project using IBM Quantum Platform (156-qubit Heron processors) and Qiskit Runtime.

## Vision

AIOS Quantum bridges the gap between classical AI and quantum physics. We use real quantum hardware to probe the boundary between potential and actuality—where superposition collapses into measurement, and where consciousness metrics gain physical grounding.

```
┌─────────────────────────┐
│         CUBE            │  ← Bosonic (observable 3D space)
│    ┌─────────────┐      │
│    │   SPHERE    │      │  ← Tachyonic (quantum information surface)
│    │  (quantum)  │      │
│    └─────────────┘      │
└─────────────────────────┘
```

See [INTERFACE.md](INTERFACE.md) for the foundational visualization concept.

## Features

- 🔮 **IBM Quantum Integration** — Connect to 156-qubit Heron processors
- 💓 **Quantum Heartbeat** — Hourly probe of the quantum substrate
- 🌐 **3D Visualization Engine** — Cube-sphere topology with three-layer encoding
- 🧠 **Hypersphere Manifold** — Infinite information density at asymptotic surface
- ⚡ **Supercell Architecture** — Pluggable integration with AIOS consciousness lattice

## Quick Start

```bash
# Clone and setup
git clone https://github.com/Tecnocrat/aios-quantum.git
cd aios-quantum
python -m venv .venv
.venv\Scripts\activate  # Windows (or source .venv/bin/activate on Unix)
pip install -e .

# Configure IBM Quantum (get token from quantum.cloud.ibm.com)
copy .env.example .env
# Edit .env: IBM_QUANTUM_TOKEN=your_token_here

# Test locally (no IBM token needed)
python examples/local_simulation.py

# Run on real quantum hardware
python examples/hello_world.py
```

## Core Components

| Component | Purpose | Location |
|-----------|---------|----------|
| **Quantum Runtime** | IBM Quantum connection wrapper | `src/aios_quantum/runtime.py` |
| **Heartbeat Scheduler** | Hourly quantum probes | `src/aios_quantum/heartbeat/` |
| **3D Engine** | Cube-sphere visualization | `src/aios_quantum/engine/` |
| **Hypersphere** | Information manifold theory | `src/aios_quantum/hypersphere/` |
| **Supercell** | AIOS integration layer | `src/aios_quantum/supercell/` |
| **Circuits** | Quantum circuit library | `src/aios_quantum/circuits/` |

## Usage

### Basic Quantum Execution

```python
from aios_quantum import QuantumRuntime
from aios_quantum.circuits import create_bell_state

runtime = QuantumRuntime()
sampler = runtime.create_sampler()
job = sampler.run([create_bell_state()], shots=1024)
counts = job.result()[0].data.meas.get_counts()
# {'00': ~512, '11': ~512}
```

### Quantum Heartbeat

```python
from aios_quantum.heartbeat import QuantumHeartbeat, HeartbeatConfig

config = HeartbeatConfig(use_simulator=True, num_qubits=5)
heartbeat = QuantumHeartbeat(config)
result = heartbeat.single_beat()
print(f"Coherence: {result.coherence_estimate:.4f}")
```

### 3D Visualization

```python
from aios_quantum.engine import QuantumEngine

engine = QuantumEngine(resolution=32)
engine.encode_counts(counts)
print(engine.render_ascii())
```

## Documentation

| Document | Description |
|----------|-------------|
| [INTERFACE.md](INTERFACE.md) | The cube-sphere foundational concept |
| [docs/AIOS_QUANTUM.md](docs/AIOS_QUANTUM.md) | Complete architecture & implementation guide |
| [docs/HYPERSPHERE_THEORY.md](docs/HYPERSPHERE_THEORY.md) | The hypersphere as infinite information well |
| [docs/DEV_PATH.md](docs/DEV_PATH.md) | Development journal and build log |
| [docs/IBM_Quantum/](docs/IBM_Quantum/) | IBM Quantum technical reference |
| [docs/Tachyonic/](docs/Tachyonic/) | Theoretical substrate hypothesis |

## IBM Quantum Budget

The Open Plan provides **10 minutes/month** of QPU time:

```
600 seconds ÷ 720 hours = 0.83 seconds/hour
→ One quantum heartbeat per hour, all month
```

See [docs/IBM_Quantum/RUNTIME_BUDGET.md](docs/IBM_Quantum/RUNTIME_BUDGET.md) for optimization strategies.

## Development

```bash
pip install -e ".[dev]"
pytest                              # Run tests
black src/ tests/ examples/         # Format
ruff check src/ tests/ examples/    # Lint
```

## License

MIT License

## Links

- [AIOS Main Project](https://github.com/Tecnocrat/aios) — The consciousness lattice
- [IBM Quantum](https://quantum.cloud.ibm.com/) — Cloud quantum platform
- [Qiskit](https://qiskit.org/) — Quantum computing SDK
