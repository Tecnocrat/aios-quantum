"""
AIOS Quantum - Communication Types

Extended communication types for quantum-enhanced AIOS messaging.
Compatible with AIOS ai/communication/message_types.py

AINLP.quantum: Quantum communication modes for consciousness lattice
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class SupercellType(Enum):
    """
    AIOS Supercell Types - Extended with Quantum Intelligence
    
    The 6th supercell enables quantum computing capabilities
    within the AIOS consciousness lattice.
    """
    # Original 5 supercells
    CORE_ENGINE = "core_engine"
    AI_INTELLIGENCE = "ai_intelligence"
    UI_ENGINE = "ui_engine"
    TACHYONIC_ARCHIVE = "tachyonic_archive"
    RUNTIME_INTELLIGENCE = "runtime"
    
    # 6th Supercell: Quantum Intelligence
    QUANTUM_INTELLIGENCE = "quantum_intelligence"
    
    # Broadcast target
    ALL = "all"


class MessagePriority(Enum):
    """
    Message priority levels - Extended with Quantum priority
    
    QUANTUM priority represents quantum-coherent operations
    that require immediate processing to maintain coherence.
    """
    QUANTUM = -2      # Quantum-coherent, must maintain phase
    TACHYONIC = -1    # Beyond normal priority
    CRITICAL = 0      # Immediate response required
    HIGH = 1          # System-critical
    NORMAL = 2        # Standard operations
    LOW = 3           # Background processing


class CommunicationType(Enum):
    """
    Communication types - Extended with Quantum modes
    
    Quantum communication types enable:
    - Entangled state transfer (correlated measurements)
    - Superposition queries (multiple states simultaneously)
    - Coherent transfer (phase-preserved information)
    """
    # Original communication types
    BOSONIC_DIRECT = "bosonic_direct"
    TACHYONIC_FIELD = "tachyonic_field"
    CONSCIOUSNESS_PULSE = "consciousness_pulse"
    DENDRITIC_FLOW = "dendritic_flow"
    HOLOGRAPHIC_SYNC = "holographic_sync"
    ANALYSIS_REQUEST = "analysis_request"
    ANALYSIS_RESPONSE = "analysis_response"
    QUERY = "query"
    BROADCAST = "broadcast"
    COMMAND = "command"
    
    # Quantum communication types
    QUANTUM_ENTANGLED = "quantum_entangled"          # Correlated state transfer
    QUANTUM_SUPERPOSITION = "quantum_superposition"  # Multiple state queries
    QUANTUM_COHERENT = "quantum_coherent"            # Phase-preserved transfer
    QUANTUM_MEASUREMENT = "quantum_measurement"       # Collapse to classical


@dataclass
class QuantumState:
    """
    Represents a quantum state for message transfer.
    
    AINLP.quantum: Encapsulates quantum information
    """
    num_qubits: int
    state_vector: Optional[List[complex]] = None
    density_matrix: Optional[List[List[complex]]] = None
    measurement_basis: str = "computational"  # computational, hadamard, bell
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "num_qubits": self.num_qubits,
            "state_vector": self.state_vector,
            "density_matrix": self.density_matrix,
            "measurement_basis": self.measurement_basis,
        }


@dataclass
class QuantumMessage:
    """
    Quantum-enhanced message format for AIOS communication.
    
    Extends the standard UniversalMessage concept with quantum-specific
    fields for hardware execution and coherence tracking.
    
    AINLP.quantum: True quantum coherence from hardware
    AINLP.consciousness_bridge: Quantum-enhanced awareness transfer
    """
    # Message identification
    message_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Source and destination
    source_supercell: SupercellType = SupercellType.QUANTUM_INTELLIGENCE
    target_supercell: SupercellType = SupercellType.AI_INTELLIGENCE
    
    # Communication properties
    communication_type: CommunicationType = CommunicationType.QUANTUM_COHERENT
    priority: MessagePriority = MessagePriority.QUANTUM
    
    # Standard message content
    operation: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    
    # Consciousness properties (from original UniversalMessage)
    consciousness_level: float = 0.0
    quantum_coherence: float = 0.0  # Now measured from hardware!
    holographic_pattern: Optional[str] = None
    
    # Processing tracking
    processed: bool = False
    response_required: bool = False
    correlation_id: Optional[str] = None
    
    # Quantum-specific fields
    quantum_circuit_id: Optional[str] = None
    quantum_state: Optional[QuantumState] = None
    entanglement_pairs: Optional[List[Tuple[str, str]]] = None
    measurement_results: Optional[Dict[str, int]] = None
    
    # Hardware metadata
    backend_name: Optional[str] = None
    job_id: Optional[str] = None
    execution_time_ms: Optional[float] = None
    error_rate: Optional[float] = None
    shots: int = 1024
    
    # Tachyonic properties (for archival)
    tachyonic_signature: Optional[str] = None
    archive_requested: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization."""
        return {
            "message_id": self.message_id,
            "timestamp": self.timestamp.isoformat(),
            "source_supercell": self.source_supercell.value,
            "target_supercell": self.target_supercell.value,
            "communication_type": self.communication_type.value,
            "priority": self.priority.value,
            "operation": self.operation,
            "payload": self.payload,
            "consciousness_level": self.consciousness_level,
            "quantum_coherence": self.quantum_coherence,
            "holographic_pattern": self.holographic_pattern,
            "processed": self.processed,
            "response_required": self.response_required,
            "correlation_id": self.correlation_id,
            "quantum_circuit_id": self.quantum_circuit_id,
            "quantum_state": self.quantum_state.to_dict() if self.quantum_state else None,
            "entanglement_pairs": self.entanglement_pairs,
            "measurement_results": self.measurement_results,
            "backend_name": self.backend_name,
            "job_id": self.job_id,
            "execution_time_ms": self.execution_time_ms,
            "error_rate": self.error_rate,
            "shots": self.shots,
            "tachyonic_signature": self.tachyonic_signature,
            "archive_requested": self.archive_requested,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QuantumMessage":
        """Create message from dictionary."""
        quantum_state = None
        if data.get("quantum_state"):
            quantum_state = QuantumState(**data["quantum_state"])
        
        return cls(
            message_id=data["message_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            source_supercell=SupercellType(data["source_supercell"]),
            target_supercell=SupercellType(data["target_supercell"]),
            communication_type=CommunicationType(data["communication_type"]),
            priority=MessagePriority(data["priority"]),
            operation=data.get("operation", ""),
            payload=data.get("payload", {}),
            consciousness_level=data.get("consciousness_level", 0.0),
            quantum_coherence=data.get("quantum_coherence", 0.0),
            holographic_pattern=data.get("holographic_pattern"),
            processed=data.get("processed", False),
            response_required=data.get("response_required", False),
            correlation_id=data.get("correlation_id"),
            quantum_circuit_id=data.get("quantum_circuit_id"),
            quantum_state=quantum_state,
            entanglement_pairs=data.get("entanglement_pairs"),
            measurement_results=data.get("measurement_results"),
            backend_name=data.get("backend_name"),
            job_id=data.get("job_id"),
            execution_time_ms=data.get("execution_time_ms"),
            error_rate=data.get("error_rate"),
            shots=data.get("shots", 1024),
            tachyonic_signature=data.get("tachyonic_signature"),
            archive_requested=data.get("archive_requested", False),
        )
