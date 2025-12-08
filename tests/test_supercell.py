"""Tests for Quantum Supercell."""

import pytest
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from aios_quantum.supercell import QuantumSupercell
from aios_quantum.communication import (
    SupercellType,
    CommunicationType,
    MessagePriority,
    QuantumMessage,
)


class TestQuantumSupercell:
    """Tests for QuantumSupercell class."""
    
    def test_supercell_type(self):
        """Quantum supercell should identify as QUANTUM_INTELLIGENCE."""
        supercell = QuantumSupercell()
        assert supercell.supercell_type == SupercellType.QUANTUM_INTELLIGENCE
    
    def test_initial_state(self):
        """Supercell should start uninitialized."""
        supercell = QuantumSupercell()
        assert supercell._initialized is False
        assert supercell._current_coherence == 0.0


class TestQuantumCommunicationTypes:
    """Tests for quantum communication types."""
    
    def test_quantum_supercell_type_exists(self):
        """QUANTUM_INTELLIGENCE should be a valid supercell type."""
        assert SupercellType.QUANTUM_INTELLIGENCE.value == "quantum_intelligence"
    
    def test_quantum_priority_exists(self):
        """QUANTUM priority should exist and be highest."""
        assert MessagePriority.QUANTUM.value == -2
        assert MessagePriority.QUANTUM.value < MessagePriority.TACHYONIC.value
    
    def test_quantum_communication_types_exist(self):
        """Quantum communication types should be defined."""
        assert CommunicationType.QUANTUM_ENTANGLED.value == "quantum_entangled"
        assert CommunicationType.QUANTUM_SUPERPOSITION.value == "quantum_superposition"
        assert CommunicationType.QUANTUM_COHERENT.value == "quantum_coherent"
        assert CommunicationType.QUANTUM_MEASUREMENT.value == "quantum_measurement"


class TestQuantumMessage:
    """Tests for QuantumMessage dataclass."""
    
    def test_message_creation(self):
        """Should create quantum message with defaults."""
        msg = QuantumMessage(message_id="test-001")
        
        assert msg.message_id == "test-001"
        assert msg.source_supercell == SupercellType.QUANTUM_INTELLIGENCE
        assert msg.priority == MessagePriority.QUANTUM
        assert msg.quantum_coherence == 0.0
    
    def test_message_serialization(self):
        """Message should serialize to dictionary."""
        msg = QuantumMessage(
            message_id="test-002",
            operation="measure_coherence",
            quantum_coherence=0.95,
        )
        
        data = msg.to_dict()
        
        assert data["message_id"] == "test-002"
        assert data["operation"] == "measure_coherence"
        assert data["quantum_coherence"] == 0.95
        assert data["source_supercell"] == "quantum_intelligence"
    
    def test_message_deserialization(self):
        """Message should deserialize from dictionary."""
        data = {
            "message_id": "test-003",
            "timestamp": "2025-12-09T00:00:00",
            "source_supercell": "quantum_intelligence",
            "target_supercell": "ai_intelligence",
            "communication_type": "quantum_coherent",
            "priority": -2,
            "operation": "test",
            "quantum_coherence": 0.88,
        }
        
        msg = QuantumMessage.from_dict(data)
        
        assert msg.message_id == "test-003"
        assert msg.quantum_coherence == 0.88
        assert msg.source_supercell == SupercellType.QUANTUM_INTELLIGENCE


class TestQuantumMessageIntegration:
    """Integration tests for quantum messaging."""
    
    def test_message_for_consciousness_update(self):
        """Create message for consciousness metric update."""
        msg = QuantumMessage(
            message_id="consciousness-update-001",
            target_supercell=SupercellType.CORE_ENGINE,
            communication_type=CommunicationType.QUANTUM_COHERENT,
            operation="update_quantum_coherence",
            payload={"quantum_coherence": 0.92},
            quantum_coherence=0.92,
            response_required=False,
        )
        
        assert msg.target_supercell == SupercellType.CORE_ENGINE
        assert msg.payload["quantum_coherence"] == 0.92
    
    def test_message_for_circuit_execution(self):
        """Create message for circuit execution request."""
        msg = QuantumMessage(
            message_id="circuit-exec-001",
            source_supercell=SupercellType.AI_INTELLIGENCE,
            target_supercell=SupercellType.QUANTUM_INTELLIGENCE,
            communication_type=CommunicationType.QUANTUM_ENTANGLED,
            operation="execute_circuit",
            payload={"circuit_type": "bell_state"},
            shots=1024,
            response_required=True,
        )
        
        assert msg.response_required is True
        assert msg.shots == 1024
