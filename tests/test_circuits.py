"""Tests for quantum circuit builders."""

import pytest
from qiskit import QuantumCircuit

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from aios_quantum.circuits import create_bell_state, create_ghz_state


class TestBellState:
    """Tests for Bell state creation."""
    
    def test_creates_circuit(self):
        """Bell state should return a QuantumCircuit."""
        circuit = create_bell_state()
        assert isinstance(circuit, QuantumCircuit)
    
    def test_has_two_qubits(self):
        """Bell state should have exactly 2 qubits."""
        circuit = create_bell_state()
        assert circuit.num_qubits == 2
    
    def test_has_measurements(self):
        """Bell state circuit should include measurements."""
        circuit = create_bell_state()
        ops = circuit.count_ops()
        assert "measure" in ops


class TestGHZState:
    """Tests for GHZ state creation."""
    
    def test_creates_circuit(self):
        """GHZ state should return a QuantumCircuit."""
        circuit = create_ghz_state()
        assert isinstance(circuit, QuantumCircuit)
    
    def test_default_three_qubits(self):
        """Default GHZ state should have 3 qubits."""
        circuit = create_ghz_state()
        assert circuit.num_qubits == 3
    
    def test_custom_qubit_count(self):
        """GHZ state should support custom qubit counts."""
        for n in [2, 4, 5, 10]:
            circuit = create_ghz_state(n)
            assert circuit.num_qubits == n
    
    def test_minimum_qubits(self):
        """GHZ state should require at least 2 qubits."""
        with pytest.raises(ValueError):
            create_ghz_state(1)
    
    def test_has_measurements(self):
        """GHZ state circuit should include measurements."""
        circuit = create_ghz_state()
        ops = circuit.count_ops()
        assert "measure" in ops
