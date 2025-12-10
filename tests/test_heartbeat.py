"""
Tests for the Quantum Heartbeat module.
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from aios_quantum.heartbeat import (
    QuantumHeartbeat,
    HeartbeatConfig,
    HeartbeatResult,
    test_heartbeat,
)


class TestHeartbeatConfig:
    """Test HeartbeatConfig dataclass."""

    def test_default_config(self):
        """Default config should have reasonable values."""
        config = HeartbeatConfig()
        assert config.interval_seconds == 3600
        assert config.num_qubits == 27
        assert config.shots == 2048
        assert config.max_monthly_seconds == 600.0

    def test_beats_remaining(self):
        """Should correctly calculate remaining beats."""
        config = HeartbeatConfig(
            max_monthly_seconds=600,
            estimated_seconds_per_beat=0.8
        )
        # Fresh start: 600/0.8 = 750
        assert config.beats_remaining(0) == 750
        # Half used: 300/0.8 = 375
        assert config.beats_remaining(300) == 375
        # Clean test: (600-592)/0.8 = 10
        assert config.beats_remaining(592) == 10

    def test_custom_config(self):
        """Should accept custom values."""
        config = HeartbeatConfig(
            num_qubits=10,
            shots=512,
            use_simulator=True,
        )
        assert config.num_qubits == 10
        assert config.shots == 512
        assert config.use_simulator is True


class TestQuantumHeartbeat:
    """Test QuantumHeartbeat class."""

    def test_initialization(self, tmp_path):
        """Should initialize with config."""
        config = HeartbeatConfig(
            use_simulator=True,
            results_dir=str(tmp_path / "results"),
        )
        heartbeat = QuantumHeartbeat(config)
        assert heartbeat.beat_count == 0
        assert heartbeat.budget_used == 0.0
        assert heartbeat.results_path.exists()

    def test_single_beat_simulator(self, tmp_path):
        """Should execute single beat on simulator."""
        config = HeartbeatConfig(
            use_simulator=True,
            num_qubits=3,  # Small for speed
            shots=100,
            results_dir=str(tmp_path / "results"),
        )
        heartbeat = QuantumHeartbeat(config)
        result = heartbeat.single_beat()

        assert result is not None
        assert isinstance(result, HeartbeatResult)
        assert result.beat_number == 0
        assert result.num_qubits == 3
        assert result.shots == 100
        assert result.backend_name == "statevector_sampler"
        assert 0 <= result.coherence_estimate <= 1
        assert 0 <= result.entropy <= 1

    def test_multiple_beats(self, tmp_path):
        """Should track beat count across multiple executions."""
        config = HeartbeatConfig(
            use_simulator=True,
            num_qubits=3,
            shots=100,
            results_dir=str(tmp_path / "results"),
        )
        heartbeat = QuantumHeartbeat(config)

        for i in range(3):
            result = heartbeat.single_beat()
            assert result.beat_number == i

        assert heartbeat.beat_count == 3
        assert len(heartbeat.results) == 3

    def test_result_persistence(self, tmp_path):
        """Should save results to disk."""
        config = HeartbeatConfig(
            use_simulator=True,
            num_qubits=3,
            shots=100,
            results_dir=str(tmp_path / "results"),
        )
        heartbeat = QuantumHeartbeat(config)
        heartbeat.single_beat()

        # Check file was created
        result_files = list(heartbeat.results_path.glob("*.json"))
        assert len(result_files) == 1

    def test_budget_tracking(self, tmp_path):
        """Should track budget usage."""
        config = HeartbeatConfig(
            use_simulator=True,
            num_qubits=3,
            shots=100,
            results_dir=str(tmp_path / "results"),
        )
        heartbeat = QuantumHeartbeat(config)
        result = heartbeat.single_beat()

        assert heartbeat.budget_used > 0
        assert result.budget_used_total > 0
        assert result.budget_remaining < config.max_monthly_seconds

    def test_dry_run_mode(self, tmp_path):
        """Dry run should not execute circuit."""
        config = HeartbeatConfig(
            use_simulator=True,
            dry_run=True,
            results_dir=str(tmp_path / "results"),
        )
        heartbeat = QuantumHeartbeat(config)
        result = heartbeat.single_beat()

        assert result is None
        assert heartbeat.beat_count == 0


class TestHeartbeatResult:
    """Test HeartbeatResult dataclass."""

    def test_to_dict(self):
        """Should convert to dictionary."""
        result = HeartbeatResult(
            beat_number=0,
            timestamp_utc="2025-01-01T00:00:00Z",
            timestamp_local="2025-01-01T00:00:00",
            backend_name="test",
            job_id="test-id",
            execution_time_seconds=0.1,
            num_qubits=5,
            circuit_depth=10,
            shots=1024,
        )
        d = result.to_dict()
        assert d["beat_number"] == 0
        assert d["backend_name"] == "test"


def test_test_heartbeat_function():
    """The convenience test function should work."""
    result = test_heartbeat()
    assert result is not None
    assert result.backend_name == "statevector_sampler"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
