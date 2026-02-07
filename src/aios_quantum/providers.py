"""
AIOS Quantum — Multi-Provider Backend System

Provides a unified interface to quantum hardware across multiple providers:
  - IBM Quantum Platform (qiskit-ibm-runtime)
  - IonQ Quantum Cloud (direct API — free simulator, Aria/Forte QPU)
  - qBraid Platform (managed access — IQM, Rigetti, QuEra, IonQ via credits)
  - Amazon Braket (amazon-braket-sdk — IonQ, Rigetti, IQM, QuEra, ...)
  - Local simulator (qiskit StatevectorSampler — always available)

Architecture:
    QuantumProvider (ABC)
        ├── IBMProvider
        ├── IonQProvider
        ├── QBraidProvider
        ├── BraketProvider
        └── SimulatorProvider

    ProviderRegistry
        └── auto-discovers available providers
        └── selects optimal provider per heartbeat
        └── failover chain: IBM → IonQ → qBraid → Braket → Simulator

The design follows AIOS degradation principles: if the preferred provider
is unavailable, the system silently degrades to the next without crashing.
"""

import os
import json
import math
import time
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


# ─── Data Structures ───────────────────────────────────────────────────────

@dataclass
class ProviderInfo:
    """Metadata about a quantum provider."""
    name: str                    # e.g., "ibm", "qbraid", "braket", "simulator"
    display_name: str            # e.g., "IBM Quantum Platform"
    is_real_hardware: bool       # True for real QPU, False for simulator
    backends: List[str] = field(default_factory=list)
    status: str = "unknown"      # "available", "unavailable", "auth_failed", "unknown"
    error: str = ""


@dataclass
class CircuitResult:
    """Unified result from any provider."""
    counts: Dict[str, int]
    shots: int
    backend_name: str
    provider_name: str           # Which provider ran this
    job_id: str
    execution_time: float        # Seconds
    num_qubits: int
    depth: int
    gate_count: int
    is_real_hardware: bool


# ─── Abstract Provider ─────────────────────────────────────────────────────

class QuantumProvider(ABC):
    """Base class for quantum hardware providers."""

    @abstractmethod
    def name(self) -> str:
        """Provider identifier (e.g., 'ibm', 'qbraid', 'braket')."""
        ...

    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider can be used (credentials present, SDK installed)."""
        ...

    @abstractmethod
    def get_backends(self) -> List[str]:
        """List available backend names."""
        ...

    @abstractmethod
    def run_circuit(
        self,
        qiskit_circuit,
        shots: int = 2048,
        backend_name: Optional[str] = None,
        optimization_level: int = 1,
    ) -> CircuitResult:
        """
        Execute a Qiskit QuantumCircuit on this provider.

        Args:
            qiskit_circuit: A qiskit.circuit.QuantumCircuit (unmeasured OK)
            shots: Number of measurement shots
            backend_name: Specific backend, or None for auto-selection
            optimization_level: Transpiler optimization level (0-3)

        Returns:
            CircuitResult with counts and metadata
        """
        ...

    def info(self) -> ProviderInfo:
        """Get provider metadata."""
        try:
            available = self.is_available()
            backends = self.get_backends() if available else []
            return ProviderInfo(
                name=self.name(),
                display_name=self.display_name(),
                is_real_hardware=True,
                backends=backends,
                status="available" if available else "unavailable",
            )
        except Exception as e:
            return ProviderInfo(
                name=self.name(),
                display_name=self.display_name(),
                is_real_hardware=True,
                status="error",
                error=str(e),
            )


# ─── IBM Provider ──────────────────────────────────────────────────────────

class IBMProvider(QuantumProvider):
    """IBM Quantum Platform via qiskit-ibm-runtime."""

    def __init__(self):
        self._service = None
        self._token = os.getenv("IBM_QUANTUM_TOKEN", "")
        self._channel = os.getenv("IBM_QUANTUM_CHANNEL", "ibm_quantum_platform")
        self._instance = os.getenv("IBM_QUANTUM_INSTANCE", "")

    def name(self) -> str:
        return "ibm"

    def display_name(self) -> str:
        return "IBM Quantum Platform"

    def is_available(self) -> bool:
        if not self._token:
            return False
        try:
            _ = self._get_service()
            return True
        except Exception:
            return False

    def _get_service(self):
        if self._service is None:
            from qiskit_ibm_runtime import QiskitRuntimeService
            kwargs = {
                "channel": self._channel,
                "token": self._token,
            }
            if self._instance:
                kwargs["instance"] = self._instance
            self._service = QiskitRuntimeService(**kwargs)
        return self._service

    def get_backends(self) -> List[str]:
        service = self._get_service()
        backends = service.backends(operational=True)
        return [b.name for b in backends]

    def run_circuit(
        self,
        qiskit_circuit,
        shots: int = 2048,
        backend_name: Optional[str] = None,
        optimization_level: int = 1,
    ) -> CircuitResult:
        from qiskit_ibm_runtime import SamplerV2
        from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

        service = self._get_service()

        if backend_name:
            backend = service.backend(backend_name)
        else:
            # Pick first operational backend
            backends = service.backends(operational=True)
            backend = backends[0] if backends else None
            if backend is None:
                raise RuntimeError("No operational IBM backends available")

        # Transpile
        pm = generate_preset_pass_manager(
            optimization_level=optimization_level, backend=backend
        )
        transpiled = pm.run(qiskit_circuit)

        # Execute
        t0 = time.time()
        sampler = SamplerV2(mode=backend)
        job = sampler.run([transpiled], shots=shots)
        result = job.result()
        elapsed = time.time() - t0

        counts = result[0].data.meas.get_counts()

        return CircuitResult(
            counts=counts,
            shots=sum(counts.values()),
            backend_name=backend.name,
            provider_name="ibm",
            job_id=job.job_id(),
            execution_time=elapsed,
            num_qubits=qiskit_circuit.num_qubits,
            depth=transpiled.depth(),
            gate_count=transpiled.size(),
            is_real_hardware=True,
        )


# ─── IonQ Direct Provider ──────────────────────────────────────────────────

class IonQProvider(QuantumProvider):
    """
    IonQ Quantum Cloud — direct access via IonQ API key.
    
    This bypasses qBraid credits entirely. IonQ offers:
      - FREE ideal simulator (unlimited)
      - Noisy simulators (Aria-1, Forte-1 noise models)
      - QPU access: Aria ($0.30/shot), Forte ($0.80/shot)
    
    Sign up free at https://cloud.ionq.com/ → Settings → API Keys
    Requires: IONQ_API_KEY environment variable.
    """

    def __init__(self):
        self._api_key = os.getenv("IONQ_API_KEY", "")
        self._provider = None

    def name(self) -> str:
        return "ionq"

    def display_name(self) -> str:
        return "IonQ Quantum Cloud"

    def is_available(self) -> bool:
        if not self._api_key:
            return False
        try:
            _ = self._get_provider()
            return True
        except Exception:
            return False

    def _get_provider(self):
        if self._provider is None:
            from qbraid.runtime.ionq import IonQProvider as _IonQP
            self._provider = _IonQP(api_key=self._api_key)
        return self._provider

    def get_backends(self) -> List[str]:
        provider = self._get_provider()
        try:
            devices = provider.get_devices()
            return [d.id for d in devices]
        except Exception:
            # IonQ always has simulator + qpu
            return ["simulator", "qpu"]

    def run_circuit(
        self,
        qiskit_circuit,
        shots: int = 2048,
        backend_name: Optional[str] = None,
        optimization_level: int = 1,
    ) -> CircuitResult:
        provider = self._get_provider()

        # Default to simulator (free)
        device_id = backend_name or "simulator"
        device = provider.get_device(device_id)

        # qBraid's IonQ wrapper handles transpilation internally
        t0 = time.time()
        job = device.run(qiskit_circuit, shots=shots)
        result = job.result()
        elapsed = time.time() - t0

        # GateModelResultData supports both .get_counts() and .measurement_counts()
        counts = result.data.get_counts()

        return CircuitResult(
            counts=counts,
            shots=sum(counts.values()),
            backend_name=device_id,
            provider_name="ionq",
            job_id=job.id,
            execution_time=elapsed,
            num_qubits=qiskit_circuit.num_qubits,
            depth=qiskit_circuit.depth(),
            gate_count=qiskit_circuit.size(),
            is_real_hardware="simulator" not in device_id.lower(),
        )


# ─── qBraid Provider ──────────────────────────────────────────────────────

class QBraidProvider(QuantumProvider):
    """
    qBraid platform — multi-vendor managed quantum access.
    
    Access IQM Garnet, Rigetti Ankaa-3, QuEra Aquila, IonQ Aria/Forte,
    and more through a single API key + credits system.
    
    Cheapest QPU: Rigetti Ankaa-3 at 0.09 credits/shot ($0.0009).
    Free credits: use access code EHNU6626 (500 credits).
    
    Requires: QBRAID_API_KEY environment variable.
    Sign up free at https://account.qbraid.com/
    """

    def __init__(self):
        self._api_key = os.getenv("QBRAID_API_KEY", "")
        self._provider = None

    def name(self) -> str:
        return "qbraid"

    def display_name(self) -> str:
        return "qBraid (Multi-Vendor)"

    def is_available(self) -> bool:
        if not self._api_key:
            return False
        try:
            _ = self._get_provider()
            return True
        except Exception:
            return False

    def _get_provider(self):
        if self._provider is None:
            from qbraid.runtime import QbraidProvider as _QBP
            self._provider = _QBP(api_key=self._api_key)
        return self._provider

    def get_backends(self) -> List[str]:
        provider = self._get_provider()
        devices = provider.get_devices(
            statuses=["ONLINE"],
        )
        return [d.id for d in devices]

    def run_circuit(
        self,
        qiskit_circuit,
        shots: int = 2048,
        backend_name: Optional[str] = None,
        optimization_level: int = 1,
    ) -> CircuitResult:
        provider = self._get_provider()

        if backend_name:
            device = provider.get_device(backend_name)
        else:
            # Get first available online device
            devices = provider.get_devices(statuses=["ONLINE"])
            if not devices:
                raise RuntimeError("No online qBraid devices available")
            device = devices[0]

        # qBraid handles transpilation internally when you submit a qiskit circuit
        t0 = time.time()
        job = device.run(qiskit_circuit, shots=shots)
        result = job.result()
        elapsed = time.time() - t0

        # GateModelResultData supports both .get_counts() and .measurement_counts()
        counts = result.data.get_counts()

        return CircuitResult(
            counts=counts,
            shots=sum(counts.values()),
            backend_name=device.id,
            provider_name="qbraid",
            job_id=job.id,
            execution_time=elapsed,
            num_qubits=qiskit_circuit.num_qubits,
            depth=qiskit_circuit.depth(),
            gate_count=qiskit_circuit.size(),
            is_real_hardware="simulator" not in device.id.lower(),
        )


# ─── Amazon Braket Provider ───────────────────────────────────────────────

class BraketProvider(QuantumProvider):
    """
    Amazon Braket — AWS quantum computing.
    
    Cheapest per-shot for Rigetti Ankaa ($0.00090/shot).
    Requires AWS credentials (aws configure or env vars).
    
    Environment:
        AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION
        BRAKET_S3_BUCKET — for result storage
    """

    # Map of Braket device ARNs to friendly names
    DEVICE_ARNS = {
        "rigetti_ankaa": "arn:aws:braket:us-west-1::device/qpu/rigetti/Ankaa-3",
        "ionq_forte": "arn:aws:braket:us-east-1::device/qpu/ionq/Forte-1",
        "iqm_garnet": "arn:aws:braket:eu-north-1::device/qpu/iqm/Garnet",
        "quera_aquila": "arn:aws:braket:us-east-1::device/qpu/quera/Aquila",
        "sv1": "arn:aws:braket:::device/quantum-simulator/amazon/sv1",
    }

    def __init__(self):
        self._has_aws = bool(
            os.getenv("AWS_ACCESS_KEY_ID") or
            Path.home().joinpath(".aws", "credentials").exists()
        )
        self._s3_bucket = os.getenv(
            "BRAKET_S3_BUCKET", "amazon-braket-aios-results"
        )

    def name(self) -> str:
        return "braket"

    def display_name(self) -> str:
        return "Amazon Braket"

    def is_available(self) -> bool:
        if not self._has_aws:
            return False
        try:
            from braket.aws import AwsSession
            session = AwsSession()
            # Quick check — will fail if creds invalid
            session.boto_session.client("braket")
            return True
        except Exception:
            return False

    def get_backends(self) -> List[str]:
        return list(self.DEVICE_ARNS.keys())

    def run_circuit(
        self,
        qiskit_circuit,
        shots: int = 2048,
        backend_name: Optional[str] = None,
        optimization_level: int = 1,
    ) -> CircuitResult:
        from braket.aws import AwsDevice, AwsQuantumTask
        from braket.circuits import Circuit as BraketCircuit
        from qbraid.transpiler import transpile as qbraid_transpile

        # Convert Qiskit → OpenQASM3 → Braket via qBraid transpiler
        qasm3_str = qbraid_transpile(qiskit_circuit, "qasm3")

        # Parse QASM3 into Braket circuit
        braket_circuit = BraketCircuit.from_ir(qasm3_str)

        # Select device
        device_key = backend_name or "rigetti_ankaa"
        arn = self.DEVICE_ARNS.get(device_key, device_key)
        device = AwsDevice(arn)

        # Execute
        s3_prefix = f"s3://{self._s3_bucket}/aios-heartbeat"
        t0 = time.time()
        task = device.run(braket_circuit, shots=shots, s3_destination_folder=s3_prefix)
        result = task.result()
        elapsed = time.time() - t0

        counts = dict(result.measurement_counts)

        return CircuitResult(
            counts=counts,
            shots=sum(counts.values()),
            backend_name=device_key,
            provider_name="braket",
            job_id=task.id,
            execution_time=elapsed,
            num_qubits=qiskit_circuit.num_qubits,
            depth=qiskit_circuit.depth(),
            gate_count=qiskit_circuit.size(),
            is_real_hardware="simulator" not in device_key,
        )


# ─── Simulator Provider (always available) ─────────────────────────────────

class SimulatorProvider(QuantumProvider):
    """
    Local Qiskit StatevectorSampler — always available, zero cost.
    No real quantum noise but keeps the heartbeat alive.
    """

    def name(self) -> str:
        return "simulator"

    def display_name(self) -> str:
        return "Local Simulator (StatevectorSampler)"

    def is_available(self) -> bool:
        return True

    def get_backends(self) -> List[str]:
        return ["statevector_sampler"]

    def run_circuit(
        self,
        qiskit_circuit,
        shots: int = 2048,
        backend_name: Optional[str] = None,
        optimization_level: int = 1,
    ) -> CircuitResult:
        from qiskit.primitives import StatevectorSampler

        sampler = StatevectorSampler()
        t0 = time.time()
        job = sampler.run([qiskit_circuit], shots=shots)
        result = job.result()
        elapsed = time.time() - t0

        counts = result[0].data.meas.get_counts()

        return CircuitResult(
            counts=counts,
            shots=sum(counts.values()),
            backend_name="statevector_sampler",
            provider_name="simulator",
            job_id="simulator",
            execution_time=elapsed,
            num_qubits=qiskit_circuit.num_qubits,
            depth=qiskit_circuit.depth(),
            gate_count=qiskit_circuit.size(),
            is_real_hardware=False,
        )


# ─── Provider Registry ────────────────────────────────────────────────────

class ProviderRegistry:
    """
    Discovers, manages, and selects quantum providers.

    Failover chain: IBM → qBraid → Braket → Simulator
    The chain ensures AIOS always has a heartbeat source.
    """

    # Default priority order — real hardware first, simulator last
    # IonQ between IBM and qBraid: IonQ has free simulator + direct QPU access
    DEFAULT_PRIORITY = ["ibm", "ionq", "qbraid", "braket", "simulator"]

    def __init__(self, priority: Optional[List[str]] = None):
        load_dotenv()  # Load .env for all providers

        self._priority = priority or self.DEFAULT_PRIORITY
        self._providers: Dict[str, QuantumProvider] = {}

        # Register all known providers
        self._register_all()

    def _register_all(self):
        """Register all provider implementations."""
        for cls in [IBMProvider, IonQProvider, QBraidProvider, BraketProvider, SimulatorProvider]:
            try:
                provider = cls()
                self._providers[provider.name()] = provider
            except Exception as e:
                logger.warning(f"Failed to instantiate {cls.__name__}: {e}")

    def get_provider(self, name: str) -> Optional[QuantumProvider]:
        """Get a specific provider by name."""
        return self._providers.get(name)

    def get_available_providers(self) -> List[QuantumProvider]:
        """Return providers that are currently available, in priority order."""
        available = []
        for name in self._priority:
            provider = self._providers.get(name)
            if provider and provider.is_available():
                available.append(provider)
        return available

    def select_provider(
        self, preferred: Optional[str] = None
    ) -> QuantumProvider:
        """
        Select the best available provider.

        Args:
            preferred: Try this provider first. Falls through priority chain
                      if unavailable.

        Returns:
            The selected QuantumProvider (always returns at least SimulatorProvider)
        """
        # Try preferred first
        if preferred:
            provider = self._providers.get(preferred)
            if provider and provider.is_available():
                logger.info(f"Using preferred provider: {provider.display_name()}")
                return provider
            logger.warning(
                f"Preferred provider '{preferred}' not available, "
                "falling through chain..."
            )

        # Walk the priority chain
        for name in self._priority:
            provider = self._providers.get(name)
            if provider and provider.is_available():
                logger.info(f"Selected provider: {provider.display_name()}")
                return provider

        # Should never happen (simulator is always available), but be safe
        logger.error("No providers available — returning simulator")
        return SimulatorProvider()

    def status(self) -> Dict[str, ProviderInfo]:
        """Get status of all registered providers."""
        result = {}
        for name in self._priority:
            provider = self._providers.get(name)
            if provider:
                result[name] = provider.info()
            else:
                result[name] = ProviderInfo(
                    name=name,
                    display_name=name,
                    is_real_hardware=False,
                    status="not_installed",
                )
        return result

    def run_heartbeat_circuit(
        self,
        qiskit_circuit,
        shots: int = 2048,
        preferred_provider: Optional[str] = None,
        preferred_backend: Optional[str] = None,
    ) -> CircuitResult:
        """
        Execute a heartbeat circuit with automatic failover.

        Tries providers in priority order until one succeeds.
        """
        tried = []
        provider = self.select_provider(preferred_provider)

        # Build attempt order: selected provider first, then remaining
        attempt_order = [provider]
        for name in self._priority:
            p = self._providers.get(name)
            if p and p is not provider and p.is_available():
                attempt_order.append(p)

        for p in attempt_order:
            try:
                logger.info(
                    f"Attempting heartbeat on {p.display_name()}..."
                )
                result = p.run_circuit(
                    qiskit_circuit,
                    shots=shots,
                    backend_name=preferred_backend if p is provider else None,
                )
                logger.info(
                    f"Heartbeat complete on {p.display_name()} "
                    f"({result.backend_name}): "
                    f"{result.execution_time:.1f}s"
                )
                return result
            except Exception as e:
                tried.append((p.name(), str(e)))
                logger.warning(
                    f"Provider {p.display_name()} failed: {e}. "
                    "Trying next..."
                )

        # All failed — this shouldn't happen since simulator never fails
        raise RuntimeError(
            f"All providers failed: {tried}"
        )


# ─── Convenience Functions ─────────────────────────────────────────────────

def provider_status() -> str:
    """Print a human-readable status of all quantum providers."""
    registry = ProviderRegistry()
    status = registry.status()
    lines = ["=== AIOS Quantum Provider Status ==="]
    for name, info in status.items():
        icon = "✓" if info.status == "available" else "✗"
        hw = "QPU" if info.is_real_hardware else "SIM"
        backends = ", ".join(info.backends[:5]) if info.backends else "—"
        if len(info.backends) > 5:
            backends += f" (+{len(info.backends) - 5} more)"
        error = f" [{info.error}]" if info.error else ""
        lines.append(
            f"  [{icon}] {info.display_name:30s} ({hw}) "
            f"backends=[{backends}]{error}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    # When run directly, print provider status
    load_dotenv()
    print(provider_status())
