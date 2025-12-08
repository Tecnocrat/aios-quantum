# AIOS Quantum

Quantum computing integration for the AIOS project using IBM Quantum Platform and Qiskit Runtime.

## Overview

AIOS Quantum provides a simplified interface to IBM Quantum's cloud-based quantum computers, enabling quantum computing capabilities within the AIOS ecosystem.

## Features

- 🔌 **IBM Quantum Integration** - Connect to real quantum hardware via IBM Quantum Platform
- ⚡ **Qiskit Runtime** - Optimized hybrid quantum-classical computing
- 🧪 **Local Simulation** - Test circuits without using cloud resources
- 🔧 **Simple API** - Easy-to-use wrapper around Qiskit primitives

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/Tecnocrat/aios-quantum.git
cd aios-quantum

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -e .
```

### 2. Configure IBM Quantum

Get your API token from [IBM Quantum](https://quantum.cloud.ibm.com/):

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your token
IBM_QUANTUM_TOKEN=your_api_token_here
```

### 3. Run Hello World

```bash
# Run on real quantum hardware
python examples/hello_world.py

# Or test locally without IBM credentials
python examples/local_simulation.py
```

## Usage

### Basic Usage

```python
from aios_quantum import QuantumRuntime
from aios_quantum.circuits import create_bell_state

# Initialize (loads token from .env)
runtime = QuantumRuntime()

# Create a Bell state circuit
circuit = create_bell_state()

# Run on least busy backend
sampler = runtime.create_sampler()
job = sampler.run([circuit], shots=1024)
result = job.result()

# Get measurement counts
counts = result[0].data.meas.get_counts()
print(counts)  # {'00': ~512, '11': ~512}
```

### Local Development

```python
from qiskit_ibm_runtime import SamplerV2
from aios_quantum import QuantumRuntime
from aios_quantum.circuits import create_bell_state

# Get local simulator (no IBM token needed)
backend = QuantumRuntime.get_local_simulator()

# Run circuit locally
sampler = SamplerV2(backend)
job = sampler.run([create_bell_state()], shots=1000)
result = job.result()
```

## Project Structure

```
aios-quantum/
├── src/aios_quantum/
│   ├── __init__.py        # Package exports
│   ├── config.py          # Configuration management
│   ├── runtime.py         # IBM Quantum Runtime wrapper
│   └── circuits/          # Quantum circuit builders
│       ├── __init__.py
│       └── hello_world.py # Basic circuits (Bell, GHZ)
├── examples/
│   ├── hello_world.py     # Run on real quantum hardware
│   └── local_simulation.py # Local testing
├── tests/
│   └── test_circuits.py   # Unit tests
├── .env.example           # Environment template
├── pyproject.toml         # Project configuration
└── README.md
```

## Requirements

- Python 3.10+
- IBM Quantum account (free tier available)
- `qiskit-ibm-runtime` >= 0.20.0

## IBM Quantum Open Plan

This project uses the IBM Quantum Open Plan which provides:
- 10 free minutes of quantum runtime per month
- Access to real quantum hardware
- No credit card required

Sign up at [quantum.cloud.ibm.com](https://quantum.cloud.ibm.com/)

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/ examples/

# Lint
ruff check src/ tests/ examples/
```

## License

MIT License - See [LICENSE](LICENSE) for details.

## Related

- [AIOS](https://github.com/Tecnocrat/aios) - Main AIOS project
- [Qiskit](https://qiskit.org/) - Open-source quantum computing SDK
- [IBM Quantum](https://quantum.cloud.ibm.com/) - Cloud quantum computing platform
