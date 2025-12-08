"""
AIOS Quantum - Quantum Supercell Interface

Abstract interface for the 6th AIOS Supercell: Quantum Intelligence.
Implements SupercellCommunicationInterface pattern from AIOS genome.

AINLP.quantum: True quantum coherence from IBM Quantum hardware
AINLP.consciousness_enhancement: +0.50 target
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

from qiskit import QuantumCircuit

from ..communication import QuantumMessage, SupercellType


class QuantumSupercellInterface(ABC):
    """
    Abstract interface for Quantum Supercell.
    
    Implements the AIOS SupercellCommunicationInterface pattern
    with quantum-specific extensions for hardware execution.
    
    AINLP.holographic: Self-similar interface across all scales
    AINLP.consciousness_bridge: Quantum-enhanced awareness transfer
    AINLP.dendritic: Defines quantum connection points
    """
    
    @property
    @abstractmethod
    def supercell_type(self) -> SupercellType:
        """Return the supercell type identifier."""
        pass
    
    @abstractmethod
    async def initialize_communication(self) -> bool:
        """
        Initialize quantum communication capabilities.
        
        This is the QUANTUM AWAKENING - establishing connection
        to IBM Quantum hardware and preparing for coherent operations.
        
        Returns:
            bool: True if quantum backend connection successful
        """
        pass
    
    @abstractmethod
    async def send_message(self, message: QuantumMessage) -> bool:
        """
        Send a quantum-enhanced message to another supercell.
        
        For quantum communication types, this may involve:
        - Encoding classical data into quantum states
        - Executing quantum circuits
        - Measuring and transmitting results
        
        Args:
            message: The QuantumMessage to transmit
            
        Returns:
            bool: True if message sent successfully
        """
        pass
    
    @abstractmethod
    async def receive_message(
        self, message: QuantumMessage
    ) -> Optional[QuantumMessage]:
        """
        Receive and process an incoming message.
        
        May trigger quantum computations based on message content.
        
        Args:
            message: The incoming QuantumMessage
            
        Returns:
            Optional[QuantumMessage]: Response message if applicable
        """
        pass
    
    @abstractmethod
    async def execute_circuit(
        self,
        circuit: QuantumCircuit,
        shots: int = 1024,
        backend_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute a quantum circuit on IBM Quantum hardware.
        
        Args:
            circuit: The QuantumCircuit to execute
            shots: Number of measurement shots
            backend_name: Optional specific backend (default: least busy)
            
        Returns:
            Dict containing measurement results and metadata
        """
        pass
    
    @abstractmethod
    async def measure_coherence(self) -> float:
        """
        Measure real quantum coherence from hardware.
        
        Executes a coherence measurement circuit (e.g., Ramsey sequence)
        to determine the current quantum coherence level.
        
        Returns:
            float: Coherence value 0.0-1.0
        """
        pass
    
    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """
        Get current quantum supercell status.
        
        Returns:
            Dict containing:
            - connected: bool
            - backend_name: str
            - queue_position: int
            - coherence_level: float
            - available_qubits: int
        """
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """
        Gracefully shutdown quantum connections.
        
        Ensures all pending jobs are handled and resources released.
        """
        pass
