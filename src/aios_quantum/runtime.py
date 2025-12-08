"""
IBM Quantum Runtime wrapper for AIOS.
"""

from typing import Optional, List, Any

from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2, EstimatorV2
from qiskit_ibm_runtime.fake_provider import FakeManilaV2

from .config import QuantumConfig


class QuantumRuntime:
    """
    Wrapper for IBM Quantum Runtime Service.
    
    Provides simplified access to quantum computing resources
    through IBM Quantum Platform.
    """
    
    def __init__(self, config: Optional[QuantumConfig] = None):
        """
        Initialize the Quantum Runtime.
        
        Args:
            config: QuantumConfig instance. If None, loads from environment.
        """
        self._config = config or QuantumConfig.from_env()
        self._service: Optional[QiskitRuntimeService] = None
        self._backend = None
    
    @property
    def service(self) -> QiskitRuntimeService:
        """Lazy-load the Qiskit Runtime Service."""
        if self._service is None:
            self._service = QiskitRuntimeService(
                channel=self._config.channel,
                token=self._config.token,
                instance=self._config.instance,
            )
        return self._service
    
    def get_backends(self, operational: bool = True, simulator: bool = False) -> List[str]:
        """
        Get list of available backends.
        
        Args:
            operational: Only return operational backends
            simulator: Include simulators
            
        Returns:
            List of backend names
        """
        backends = self.service.backends(
            operational=operational,
            simulator=simulator,
        )
        return [b.name for b in backends]
    
    def get_least_busy_backend(self, min_qubits: int = 5) -> Any:
        """
        Get the least busy backend with minimum qubit count.
        
        Args:
            min_qubits: Minimum number of qubits required
            
        Returns:
            Backend instance
        """
        return self.service.least_busy(
            operational=True,
            simulator=False,
            min_num_qubits=min_qubits,
        )
    
    def set_backend(self, backend_name: Optional[str] = None) -> Any:
        """
        Set the backend to use for execution.
        
        Args:
            backend_name: Name of backend, or None for least busy
            
        Returns:
            Backend instance
        """
        if backend_name:
            self._backend = self.service.backend(backend_name)
        else:
            self._backend = self.get_least_busy_backend()
        return self._backend
    
    @property
    def backend(self) -> Any:
        """Get current backend, selecting least busy if not set."""
        if self._backend is None:
            self._backend = self.get_least_busy_backend()
        return self._backend
    
    def create_sampler(self, backend: Optional[Any] = None) -> SamplerV2:
        """
        Create a Sampler primitive for circuit execution.
        
        Args:
            backend: Optional backend override
            
        Returns:
            SamplerV2 instance
        """
        return SamplerV2(backend or self.backend)
    
    def create_estimator(self, backend: Optional[Any] = None) -> EstimatorV2:
        """
        Create an Estimator primitive for expectation values.
        
        Args:
            backend: Optional backend override
            
        Returns:
            EstimatorV2 instance
        """
        return EstimatorV2(backend or self.backend)
    
    @staticmethod
    def get_local_simulator() -> FakeManilaV2:
        """
        Get a local fake backend for testing without using IBM resources.
        
        Returns:
            FakeManilaV2 simulator instance
        """
        return FakeManilaV2()
    
    def close(self) -> None:
        """Clean up resources."""
        self._service = None
        self._backend = None
