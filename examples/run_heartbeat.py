"""
Quantum Heartbeat Example

Demonstrates the heartbeat scheduler in different modes.

Usage:
    # Test mode (single beat, simulator):
    python examples/run_heartbeat.py

    # Multiple beats simulation:
    python examples/run_heartbeat.py --beats 5

    # Real hardware (uses IBM Quantum budget!):
    python examples/run_heartbeat.py --real

    # Full production mode (runs continuously):
    python examples/run_heartbeat.py --production
"""

import argparse
import sys
sys.path.insert(0, 'src')

from aios_quantum.heartbeat import (
    QuantumHeartbeat,
    HeartbeatConfig,
    test_heartbeat,
)


def run_test_mode():
    """Quick test: single beat on simulator."""
    print("\n" + "=" * 60)
    print("QUANTUM HEARTBEAT - TEST MODE")
    print("=" * 60)
    print("Running single heartbeat on local simulator...")
    print()

    result = test_heartbeat()

    if result:
        print("\n" + "-" * 40)
        print("ANALYSIS")
        print("-" * 40)
        print(f"High coherence ({result.coherence_estimate:.2%}) means")
        print("measurements clustered around dominant states.")
        print()
        print(f"Low entropy ({result.entropy:.4f}) indicates")
        print("information is concentrated, not dispersed.")
        print()
        print("This is the quantum signature we're recording.")
        print("Each hour, a new beat adds to our tachyonic archive.")


def run_multiple_beats(num_beats: int):
    """Run multiple heartbeats in rapid succession (for testing)."""
    print("\n" + "=" * 60)
    print(f"QUANTUM HEARTBEAT - {num_beats} BEATS")
    print("=" * 60)

    config = HeartbeatConfig(
        use_simulator=True,
        num_qubits=5,
        shots=1024,
        interval_seconds=1,  # 1 second between beats for testing
    )

    heartbeat = QuantumHeartbeat(config)
    heartbeat.start(max_beats=num_beats)

    print("\n" + "-" * 40)
    print("SUMMARY")
    print("-" * 40)
    print(f"Total beats: {len(heartbeat.results)}")

    if heartbeat.results:
        avg_coherence = sum(r.coherence_estimate for r in heartbeat.results)
        avg_coherence /= len(heartbeat.results)
        print(f"Average coherence: {avg_coherence:.4f}")

        # Show evolution
        print("\nCoherence evolution:")
        for r in heartbeat.results:
            bar = "█" * int(r.coherence_estimate * 40)
            print(f"  Beat {r.beat_number:2d}: {bar} {r.coherence_estimate:.4f}")


def run_real_hardware():
    """Run on real IBM Quantum hardware (uses budget!)."""
    print("\n" + "=" * 60)
    print("QUANTUM HEARTBEAT - REAL HARDWARE")
    print("=" * 60)
    print()
    print("⚠️  WARNING: This uses your IBM Quantum budget!")
    print("    Estimated cost: ~0.8 seconds per beat")
    print()

    confirm = input("Continue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Aborted.")
        return

    config = HeartbeatConfig(
        use_simulator=False,
        num_qubits=27,
        shots=2048,
    )

    heartbeat = QuantumHeartbeat(config)
    result = heartbeat.single_beat()

    if result:
        print("\n" + "-" * 40)
        print("REAL QUANTUM RESULT")
        print("-" * 40)
        print(f"Backend: {result.backend_name}")
        print(f"Job ID: {result.job_id}")
        print(f"Execution time: {result.execution_time_seconds:.2f}s")
        print(f"Coherence: {result.coherence_estimate:.4f}")
        print(f"Entropy: {result.entropy:.4f}")
        print(f"Budget remaining: {result.budget_remaining:.1f}s")


def run_production():
    """Run in production mode (continuous, hourly beats)."""
    print("\n" + "=" * 60)
    print("QUANTUM HEARTBEAT - PRODUCTION MODE")
    print("=" * 60)
    print()
    print("This will run continuously, one beat per hour.")
    print("Press Ctrl+C to stop.")
    print()

    # Default to simulator for safety
    use_real = input("Use real hardware? (yes/no, default=no): ")
    use_simulator = use_real.lower() != 'yes'

    config = HeartbeatConfig(
        use_simulator=use_simulator,
        num_qubits=27 if not use_simulator else 10,
        shots=2048,
        interval_seconds=3600,  # 1 hour
    )

    heartbeat = QuantumHeartbeat(config)
    heartbeat.start()


def main():
    parser = argparse.ArgumentParser(
        description="Quantum Heartbeat - The pulse of AIOS Quantum"
    )
    parser.add_argument(
        '--beats', type=int,
        help="Run multiple beats in quick succession"
    )
    parser.add_argument(
        '--real', action='store_true',
        help="Use real IBM Quantum hardware"
    )
    parser.add_argument(
        '--production', action='store_true',
        help="Run in production mode (continuous)"
    )

    args = parser.parse_args()

    if args.production:
        run_production()
    elif args.real:
        run_real_hardware()
    elif args.beats:
        run_multiple_beats(args.beats)
    else:
        run_test_mode()


if __name__ == "__main__":
    main()
