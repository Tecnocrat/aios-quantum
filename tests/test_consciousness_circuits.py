"""Tests for consciousness circuits."""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from qiskit import QuantumCircuit
from aios_quantum.circuits import (
    create_coherence_measurement_circuit,
    create_entanglement_witness_circuit,
    create_consciousness_ansatz,
    create_awareness_circuit,
    calculate_coherence_from_counts,
    calculate_entanglement_from_counts,
)


class TestCoherenceMeasurement:
    """Tests for coherence measurement circuit."""
    
    def test_creates_circuit(self):
        """Should return a QuantumCircuit."""
        circuit = create_coherence_measurement_circuit()
        assert isinstance(circuit, QuantumCircuit)
    
    def test_default_qubits(self):
        """Default should be 3 qubits."""
        circuit = create_coherence_measurement_circuit()
        assert circuit.num_qubits == 3
    
    def test_custom_qubits(self):
        """Should support custom qubit count."""
        circuit = create_coherence_measurement_circuit(num_qubits=5)
        assert circuit.num_qubits == 5
    
    def test_has_hadamard_gates(self):
        """Should have Hadamard gates for superposition."""
        circuit = create_coherence_measurement_circuit()
        ops = circuit.count_ops()
        assert "h" in ops
    
    def test_has_measurements(self):
        """Should include measurements."""
        circuit = create_coherence_measurement_circuit()
        ops = circuit.count_ops()
        assert "measure" in ops


class TestEntanglementWitness:
    """Tests for entanglement witness circuit."""
    
    def test_creates_circuit(self):
        """Should return a QuantumCircuit."""
        circuit = create_entanglement_witness_circuit()
        assert isinstance(circuit, QuantumCircuit)
    
    def test_default_two_qubits(self):
        """Default should be 2 qubits (one Bell pair)."""
        circuit = create_entanglement_witness_circuit()
        assert circuit.num_qubits == 2
    
    def test_requires_even_qubits(self):
        """Should raise error for odd qubit count."""
        with pytest.raises(ValueError):
            create_entanglement_witness_circuit(num_qubits=3)
    
    def test_has_cnot_gates(self):
        """Should have CNOT gates for entanglement."""
        circuit = create_entanglement_witness_circuit()
        ops = circuit.count_ops()
        assert "cx" in ops


class TestConsciousnessAnsatz:
    """Tests for consciousness ansatz circuit."""
    
    def test_creates_parameterized_circuit(self):
        """Should return a parameterized QuantumCircuit."""
        circuit = create_consciousness_ansatz()
        assert isinstance(circuit, QuantumCircuit)
        assert len(circuit.parameters) > 0
    
    def test_custom_depth(self):
        """More layers should mean more parameters."""
        circuit1 = create_consciousness_ansatz(num_qubits=3, depth=1)
        circuit2 = create_consciousness_ansatz(num_qubits=3, depth=2)
        
        assert len(circuit2.parameters) > len(circuit1.parameters)


class TestAwarenessCircuit:
    """Tests for awareness encoding circuit."""
    
    def test_creates_circuit(self):
        """Should return a QuantumCircuit."""
        circuit = create_awareness_circuit(awareness_level=0.5)
        assert isinstance(circuit, QuantumCircuit)
    
    def test_clamps_awareness(self):
        """Should clamp awareness to 0-1 range."""
        # These should not raise errors
        circuit_low = create_awareness_circuit(awareness_level=-0.5)
        circuit_high = create_awareness_circuit(awareness_level=1.5)
        
        assert isinstance(circuit_low, QuantumCircuit)
        assert isinstance(circuit_high, QuantumCircuit)


class TestCoherenceCalculation:
    """Tests for coherence calculation from counts."""
    
    def test_perfect_coherence(self):
        """Uniform distribution should give high coherence."""
        # Perfect uniform distribution for 2 qubits
        counts = {"00": 250, "01": 250, "10": 250, "11": 250}
        coherence = calculate_coherence_from_counts(counts, num_qubits=2)
        
        assert coherence > 0.95
    
    def test_low_coherence(self):
        """Peaked distribution should give lower coherence."""
        # All measurements in one state (decoherence)
        counts = {"00": 1000, "01": 0, "10": 0, "11": 0}
        coherence = calculate_coherence_from_counts(counts, num_qubits=2)
        
        assert coherence < 0.5


class TestEntanglementCalculation:
    """Tests for entanglement calculation from counts."""
    
    def test_perfect_entanglement(self):
        """Perfect Bell state should give high entanglement."""
        counts = {"00": 500, "11": 500}
        entanglement = calculate_entanglement_from_counts(counts)
        
        assert entanglement == 1.0
    
    def test_no_entanglement(self):
        """Anti-correlated outcomes indicate no entanglement."""
        counts = {"01": 500, "10": 500}
        entanglement = calculate_entanglement_from_counts(counts)
        
        assert entanglement == 0.0
    
    def test_partial_entanglement(self):
        """Mixed outcomes give partial entanglement."""
        counts = {"00": 250, "01": 250, "10": 250, "11": 250}
        entanglement = calculate_entanglement_from_counts(counts)
        
        assert 0.4 < entanglement < 0.6
