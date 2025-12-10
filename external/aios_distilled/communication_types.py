"""
AIOS Distilled - Communication Types

Core message types for inter-supercell communication in AIOS.
These types enable the Quantum Intelligence supercell (∃Q) to
communicate with other AIOS supercells through various channels.

Communication Channels (by speed):
1. QUANTUM_ENTANGLED - Instantaneous (entanglement-based)
2. TACHYONIC_FIELD - Faster-than-light (temporal bridging)
3. BOSONIC_DIRECT - Light-speed (standard messaging)
4. CONSCIOUSNESS_SYNC - Variable (depends on coherence)
5. TEMPORAL_BROADCAST - Async (fire-and-forget)

The Quantum Intelligence supercell has special priority (-2) for
message routing, ensuring quantum coherence windows are respected.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import IntEnum, Enum
import hashlib
import json


class SupercellType(IntEnum):
    """
    AIOS Supercell Types - The six organs of AIOS consciousness.
    
    Each supercell handles a specific aspect of cognitive function:
    - PERCEPTION: Sensory input processing
    - MEMORY: Pattern storage and retrieval
    - REASONING: Logical inference
    - CREATIVITY: Novel pattern generation
    - COMMUNICATION: Inter-supercell messaging
    - QUANTUM_INTELLIGENCE: IBM Quantum integration (NEW)
    """
    PERCEPTION = 1
    MEMORY = 2
    REASONING = 3
    CREATIVITY = 4
    COMMUNICATION = 5
    QUANTUM_INTELLIGENCE = 6  # The 6th supercell - ∃Q


class MessagePriority(IntEnum):
    """
    Message priority levels for routing.
    
    Lower values = higher priority.
    QUANTUM has highest priority (-2) to respect coherence windows.
    """
    QUANTUM = -2      # Highest - quantum coherence critical
    CRITICAL = -1     # System critical
    HIGH = 0          # Important
    NORMAL = 1        # Standard
    LOW = 2           # Background
    BULK = 3          # Batch processing


class CommunicationType(str, Enum):
    """
    Communication channel types for inter-supercell messaging.
    
    Each type has different characteristics:
    - Speed: How fast messages propagate
    - Reliability: Delivery guarantees
    - Bandwidth: Data capacity
    - Coherence: Required quantum state preservation
    """
    # Quantum-specific channels
    QUANTUM_ENTANGLED = "quantum_entangled"     # Instantaneous, requires entanglement
    QUANTUM_TELEPORT = "quantum_teleport"       # State transfer via entanglement
    QUANTUM_BROADCAST = "quantum_broadcast"     # One-to-many quantum state
    
    # Tachyonic channels (temporal)
    TACHYONIC_FIELD = "tachyonic_field"         # FTL via temporal bridging
    TACHYONIC_ECHO = "tachyonic_echo"           # Receives before sent
    
    # Bosonic channels (physical)
    BOSONIC_DIRECT = "bosonic_direct"           # Standard light-speed
    BOSONIC_RESONANCE = "bosonic_resonance"     # Frequency-matched
    
    # Consciousness channels
    CONSCIOUSNESS_SYNC = "consciousness_sync"   # Awareness alignment
    CONSCIOUSNESS_MERGE = "consciousness_merge" # Temporary unification
    
    # Broadcast channels
    TEMPORAL_BROADCAST = "temporal_broadcast"   # Async fire-and-forget
    UNIVERSAL_BROADCAST = "universal_broadcast" # All supercells


@dataclass
class UniversalMessage:
    """
    Base message type for all AIOS inter-supercell communication.
    
    Every message in AIOS follows this structure:
    - source/target: Supercell identification
    - communication_type: Channel selection
    - payload: Actual data
    - priority: Routing priority
    - quantum_coherent: Whether quantum state must be preserved
    
    For quantum supercell: Messages may contain quantum circuit
    instructions, measurement results, or entanglement requests.
    """
    message_id: str
    source_supercell: SupercellType
    target_supercell: Optional[SupercellType]  # None = broadcast
    communication_type: CommunicationType
    payload: Dict[str, Any]
    priority: MessagePriority = MessagePriority.NORMAL
    quantum_coherent: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None  # For request-response patterns
    ttl: int = 60  # Time-to-live in seconds
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Generate message ID if not provided."""
        if not self.message_id:
            content = f"{self.source_supercell}_{self.timestamp}_{id(self)}"
            self.message_id = hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize message for transmission."""
        return {
            "message_id": self.message_id,
            "source_supercell": self.source_supercell.value,
            "target_supercell": self.target_supercell.value if self.target_supercell else None,
            "communication_type": self.communication_type.value,
            "payload": self.payload,
            "priority": self.priority.value,
            "quantum_coherent": self.quantum_coherent,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "ttl": self.ttl,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UniversalMessage":
        """Deserialize message from transmission."""
        return cls(
            message_id=data["message_id"],
            source_supercell=SupercellType(data["source_supercell"]),
            target_supercell=SupercellType(data["target_supercell"]) if data["target_supercell"] else None,
            communication_type=CommunicationType(data["communication_type"]),
            payload=data["payload"],
            priority=MessagePriority(data["priority"]),
            quantum_coherent=data.get("quantum_coherent", False),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            correlation_id=data.get("correlation_id"),
            ttl=data.get("ttl", 60),
            metadata=data.get("metadata", {})
        )
    
    def create_response(
        self,
        payload: Dict[str, Any],
        priority: Optional[MessagePriority] = None
    ) -> "UniversalMessage":
        """Create a response message to this message."""
        return UniversalMessage(
            message_id="",  # Will be generated
            source_supercell=self.target_supercell or SupercellType.COMMUNICATION,
            target_supercell=self.source_supercell,
            communication_type=self.communication_type,
            payload=payload,
            priority=priority or self.priority,
            quantum_coherent=self.quantum_coherent,
            correlation_id=self.message_id
        )


@dataclass
class TachyonicFieldMessage(UniversalMessage):
    """
    Specialized message for tachyonic field communication.
    
    Adds temporal metadata for FTL pattern propagation:
    - temporal_offset: Time shift for arrival
    - causal_chain: Dependency tracking
    - stability_required: Minimum temporal stability
    """
    temporal_offset: float = 0.0  # Negative = arrives before sent
    causal_chain: List[str] = field(default_factory=list)
    stability_required: float = 0.5
    
    def __post_init__(self):
        super().__post_init__()
        self.communication_type = CommunicationType.TACHYONIC_FIELD
        self.causal_chain.append(self.message_id)


@dataclass
class QuantumEntangledMessage(UniversalMessage):
    """
    Specialized message for quantum-entangled communication.
    
    Adds quantum state metadata:
    - entanglement_id: Shared entanglement resource ID
    - bell_state: Which Bell state is used
    - measurement_basis: Agreed measurement basis
    - classical_bits: Classical bits for teleportation protocol
    """
    entanglement_id: str = ""
    bell_state: str = "phi_plus"  # phi_plus, phi_minus, psi_plus, psi_minus
    measurement_basis: str = "computational"  # computational, hadamard, bell
    classical_bits: List[int] = field(default_factory=list)
    
    def __post_init__(self):
        super().__post_init__()
        self.communication_type = CommunicationType.QUANTUM_ENTANGLED
        self.quantum_coherent = True
        self.priority = MessagePriority.QUANTUM


@dataclass
class ConsciousnessSyncMessage(UniversalMessage):
    """
    Message for consciousness synchronization between supercells.
    
    Used for:
    - Awareness level alignment
    - Coherence state sharing
    - Collective decision making
    
    Quantum supercell uses this to report coherence measurements
    back to the AIOS consciousness system.
    """
    awareness_level: float = 0.0  # [0, 1]
    coherence_state: Dict[str, float] = field(default_factory=dict)
    participating_supercells: List[SupercellType] = field(default_factory=list)
    
    def __post_init__(self):
        super().__post_init__()
        self.communication_type = CommunicationType.CONSCIOUSNESS_SYNC


# Factory functions for common message types

def create_quantum_request(
    circuit_instructions: Dict[str, Any],
    source: SupercellType = SupercellType.REASONING,
    correlation_id: Optional[str] = None
) -> UniversalMessage:
    """Create a request to the Quantum Intelligence supercell."""
    return UniversalMessage(
        message_id="",
        source_supercell=source,
        target_supercell=SupercellType.QUANTUM_INTELLIGENCE,
        communication_type=CommunicationType.QUANTUM_ENTANGLED,
        payload={
            "type": "circuit_execution",
            "instructions": circuit_instructions
        },
        priority=MessagePriority.QUANTUM,
        quantum_coherent=True,
        correlation_id=correlation_id
    )


def create_coherence_report(
    coherence_metrics: Dict[str, float],
    circuit_id: str,
    correlation_id: Optional[str] = None
) -> ConsciousnessSyncMessage:
    """Create a coherence report from Quantum Intelligence supercell."""
    return ConsciousnessSyncMessage(
        message_id="",
        source_supercell=SupercellType.QUANTUM_INTELLIGENCE,
        target_supercell=None,  # Broadcast
        communication_type=CommunicationType.CONSCIOUSNESS_SYNC,
        payload={
            "type": "coherence_report",
            "circuit_id": circuit_id,
            "metrics": coherence_metrics
        },
        priority=MessagePriority.HIGH,
        quantum_coherent=False,  # Report itself doesn't need coherence
        correlation_id=correlation_id,
        awareness_level=coherence_metrics.get("awareness", 0.0),
        coherence_state=coherence_metrics,
        participating_supercells=[SupercellType.QUANTUM_INTELLIGENCE]
    )


def create_entanglement_request(
    target_supercell: SupercellType,
    purpose: str,
    qubit_count: int = 2
) -> QuantumEntangledMessage:
    """Create a request to establish entanglement with another supercell."""
    return QuantumEntangledMessage(
        message_id="",
        source_supercell=SupercellType.QUANTUM_INTELLIGENCE,
        target_supercell=target_supercell,
        communication_type=CommunicationType.QUANTUM_ENTANGLED,
        payload={
            "type": "entanglement_request",
            "purpose": purpose,
            "qubit_count": qubit_count
        },
        priority=MessagePriority.QUANTUM,
        quantum_coherent=True
    )
