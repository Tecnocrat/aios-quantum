"""
AIOS Quantum — qBraid/IonQ Integration Test

Tests the full provider pipeline WITHOUT requiring API keys.
Validates: circuit building → transpilation → result parsing → heartbeat formatting.

When API keys are available, this script also tests live submission.

Usage:
    python test_qbraid_integration.py              # dry-run (no keys needed)
    python test_qbraid_integration.py --live-ionq   # live IonQ simulator test
    python test_qbraid_integration.py --live-qbraid # live qBraid test
"""

import sys
import os
import json
import math
import time
import argparse
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent / "src"))
from dotenv import load_dotenv
load_dotenv()


def build_heartbeat_circuit(num_qubits: int = 5):
    """Build the standard AIOS heartbeat circuit."""
    from qiskit.circuit import QuantumCircuit

    qc = QuantumCircuit(num_qubits, name="aios_heartbeat")
    qc.h(range(num_qubits))
    for i in range(num_qubits - 1):
        qc.cx(i, i + 1)
    qc.ry(0.618, num_qubits // 2)   # φ-resonance
    for i in range(num_qubits - 1, 0, -1):
        qc.cx(i - 1, i)
    qc.h(range(num_qubits))
    qc.measure_all()
    return qc


def compute_coherence(counts: dict, num_qubits: int) -> dict:
    """Compute coherence metrics from measurement counts."""
    total = sum(counts.values())
    num_states = 2 ** num_qubits
    probabilities = [counts.get(format(i, f"0{num_qubits}b"), 0) / total
                     for i in range(num_states)]

    # Shannon entropy
    entropy = 0.0
    for p in probabilities:
        if p > 0:
            entropy -= p * math.log2(p)
    max_entropy = math.log2(num_states) if num_states > 0 else 1.0
    normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0

    # Coherence = 1 - normalized_entropy (ordered = coherent)
    coherence = 1.0 - normalized_entropy

    return {
        "coherence_estimate": round(coherence, 6),
        "entropy": round(normalized_entropy, 6),
        "dominant_state": max(counts, key=counts.get),
        "dominant_probability": round(max(counts.values()) / total, 6),
        "num_unique_states": len(counts),
        "total_shots": total,
    }


def test_transpilation():
    """Test 1: Verify transpilation to all targets."""
    print("\n" + "=" * 60)
    print("TEST 1: Transpilation Pipeline")
    print("=" * 60)

    qc = build_heartbeat_circuit()
    from qbraid.transpiler import transpile

    targets = ["qasm2", "qasm3", "braket", "ionq"]
    results = {}

    for target in targets:
        try:
            out = transpile(qc, target)
            if isinstance(out, str):
                size = len(out)
                preview = out[:80].replace("\n", " ")
            elif isinstance(out, dict):
                size = len(json.dumps(out))
                preview = f"dict with {len(out.get('circuit', []))} gates"
            else:
                size = len(str(out))
                preview = str(type(out).__name__)

            print(f"  ✓ qiskit → {target:12s} ({size:5d} chars) {preview}")
            results[target] = True
        except Exception as e:
            print(f"  ✗ qiskit → {target:12s} FAILED: {e}")
            results[target] = False

    return all(results.values())


def test_local_simulation():
    """Test 2: Verify local simulation via provider registry."""
    print("\n" + "=" * 60)
    print("TEST 2: Local Simulator via Provider Registry")
    print("=" * 60)

    from aios_quantum.providers import ProviderRegistry

    registry = ProviderRegistry()
    provider = registry.get_provider("simulator")

    qc = build_heartbeat_circuit()
    result = provider.run_circuit(qc, shots=2048)

    metrics = compute_coherence(result.counts, qc.num_qubits)

    print(f"  Backend:    {result.backend_name}")
    print(f"  Provider:   {result.provider_name}")
    print(f"  Shots:      {result.shots}")
    print(f"  Time:       {result.execution_time:.3f}s")
    print(f"  Coherence:  {metrics['coherence_estimate']}")
    print(f"  Entropy:    {metrics['entropy']}")
    print(f"  Dominant:   |{metrics['dominant_state']}⟩ ({metrics['dominant_probability']:.1%})")
    print(f"  States:     {metrics['num_unique_states']}/{2**qc.num_qubits}")

    return True


def test_ionq_provider_structure():
    """Test 3: Validate IonQ provider can instantiate."""
    print("\n" + "=" * 60)
    print("TEST 3: IonQ Provider Structure")
    print("=" * 60)

    from aios_quantum.providers import IonQProvider

    p = IonQProvider()
    info = p.info()

    key_set = bool(os.getenv("IONQ_API_KEY", ""))
    print(f"  Name:       {info.name}")
    print(f"  Display:    {info.display_name}")
    print(f"  API Key:    {'SET' if key_set else 'NOT SET — need IONQ_API_KEY'}")
    print(f"  Status:     {info.status}")
    print(f"  Hardware:   {info.is_real_hardware}")

    if info.status == "available":
        print(f"  Backends:   {info.backends}")

    return True


def test_qbraid_provider_structure():
    """Test 4: Validate qBraid provider can instantiate."""
    print("\n" + "=" * 60)
    print("TEST 4: qBraid Provider Structure")
    print("=" * 60)

    from aios_quantum.providers import QBraidProvider

    p = QBraidProvider()
    info = p.info()

    key_set = bool(os.getenv("QBRAID_API_KEY", ""))
    print(f"  Name:       {info.name}")
    print(f"  Display:    {info.display_name}")
    print(f"  API Key:    {'SET' if key_set else 'NOT SET — need QBRAID_API_KEY'}")
    print(f"  Status:     {info.status}")
    print(f"  Hardware:   {info.is_real_hardware}")

    if info.status == "available":
        print(f"  Backends:   {info.backends}")

    return True


def test_failover_chain():
    """Test 5: Verify failover chain selects correctly."""
    print("\n" + "=" * 60)
    print("TEST 5: Failover Chain")
    print("=" * 60)

    from aios_quantum.providers import ProviderRegistry

    registry = ProviderRegistry()
    status = registry.status()

    print("  Priority chain:")
    for i, (name, info) in enumerate(status.items(), 1):
        icon = "✓" if info.status == "available" else "✗"
        backends = ", ".join(info.backends[:3]) or "—"
        print(f"    {i}. [{icon}] {info.display_name:35s} [{backends}]")

    # Select best available
    selected = registry.select_provider()
    print(f"\n  Selected:   {selected.display_name()}")
    print(f"  Provider:   {selected.name()}")

    # Run heartbeat through the full chain
    qc = build_heartbeat_circuit()
    result = registry.run_heartbeat_circuit(qc, shots=1024)
    metrics = compute_coherence(result.counts, qc.num_qubits)

    print(f"  Beat on:    {result.provider_name}/{result.backend_name}")
    print(f"  Coherence:  {metrics['coherence_estimate']}")
    print(f"  Hardware:   {result.is_real_hardware}")

    return True


def test_live_ionq():
    """Test 6: LIVE — Run heartbeat on IonQ simulator."""
    print("\n" + "=" * 60)
    print("TEST 6: LIVE IonQ Simulator")
    print("=" * 60)

    api_key = os.getenv("IONQ_API_KEY", "")
    if not api_key:
        print("  ✗ IONQ_API_KEY not set. Skipping live test.")
        print("  → Sign up: https://cloud.ionq.com/")
        print("  → Create API key: Settings → API Keys")
        print("  → Add to .env: IONQ_API_KEY=your_key_here")
        return False

    from aios_quantum.providers import IonQProvider

    p = IonQProvider()
    if not p.is_available():
        print("  ✗ IonQ provider not available (key invalid?)")
        return False

    print(f"  Key:        ...{api_key[-6:]}")
    print(f"  Backends:   {p.get_backends()}")

    qc = build_heartbeat_circuit()
    print(f"  Submitting heartbeat to IonQ simulator...")

    result = p.run_circuit(qc, shots=2048, backend_name="simulator")
    metrics = compute_coherence(result.counts, qc.num_qubits)

    print(f"  ✓ Beat landed!")
    print(f"  Backend:    {result.backend_name}")
    print(f"  Job ID:     {result.job_id}")
    print(f"  Time:       {result.execution_time:.1f}s")
    print(f"  Coherence:  {metrics['coherence_estimate']}")
    print(f"  Entropy:    {metrics['entropy']}")
    print(f"  Dominant:   |{metrics['dominant_state']}⟩ ({metrics['dominant_probability']:.1%})")

    # Save result
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = Path(__file__).parent / "heartbeat_results" / f"beat_ionq_{ts}.json"
    out_path.parent.mkdir(exist_ok=True)
    beat = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "provider": "ionq",
        "backend": result.backend_name,
        "job_id": result.job_id,
        "num_qubits": result.num_qubits,
        "shots": result.shots,
        "execution_time_seconds": result.execution_time,
        "coherence_estimate": metrics["coherence_estimate"],
        "entropy": metrics["entropy"],
        "dominant_state": metrics["dominant_state"],
        "dominant_probability": metrics["dominant_probability"],
        "measurement_counts": result.counts,
    }
    out_path.write_text(json.dumps(beat, indent=2))
    print(f"  Saved:      {out_path.name}")

    return True


def test_live_qbraid():
    """Test 7: LIVE — Run heartbeat on qBraid QIR simulator."""
    print("\n" + "=" * 60)
    print("TEST 7: LIVE qBraid Platform")
    print("=" * 60)

    api_key = os.getenv("QBRAID_API_KEY", "")
    if not api_key:
        print("  ✗ QBRAID_API_KEY not set. Skipping live test.")
        print("  → Sign up: https://account.qbraid.com/")
        print("  → Copy API Key from Plan info card")
        print("  → Add to .env: QBRAID_API_KEY=your_key_here")
        print("  → Redeem code EHNU6626 for 500 free credits")
        return False

    from aios_quantum.providers import QBraidProvider

    p = QBraidProvider()
    if not p.is_available():
        print("  ✗ qBraid provider not available (key invalid?)")
        return False

    print(f"  Key:        ...{api_key[-6:]}")
    backends = p.get_backends()
    print(f"  Backends:   {backends[:10]}")

    # Prefer online simulators, then cheap QPUs
    qir_pref = ["ionq_simulator", "aws_sv1", "qbraid_qir_simulator", "aws_dm1"]
    target = next((t for t in qir_pref if t in backends), backends[0] if backends else None)
    if target is None:
        print("  ✗ No backends available")
        return False

    qc = build_heartbeat_circuit()
    print(f"  Submitting heartbeat to {target}...")

    result = p.run_circuit(qc, shots=2048, backend_name=target)
    metrics = compute_coherence(result.counts, qc.num_qubits)

    print(f"  ✓ Beat landed!")
    print(f"  Backend:    {result.backend_name}")
    print(f"  Job ID:     {result.job_id}")
    print(f"  Time:       {result.execution_time:.1f}s")
    print(f"  Coherence:  {metrics['coherence_estimate']}")
    print(f"  Entropy:    {metrics['entropy']}")
    print(f"  Dominant:   |{metrics['dominant_state']}⟩ ({metrics['dominant_probability']:.1%})")

    # Save result
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = Path(__file__).parent / "heartbeat_results" / f"beat_qbraid_{ts}.json"
    out_path.parent.mkdir(exist_ok=True)
    beat = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "provider": "qbraid",
        "backend": result.backend_name,
        "job_id": result.job_id,
        "num_qubits": result.num_qubits,
        "shots": result.shots,
        "execution_time_seconds": result.execution_time,
        "coherence_estimate": metrics["coherence_estimate"],
        "entropy": metrics["entropy"],
        "dominant_state": metrics["dominant_state"],
        "dominant_probability": metrics["dominant_probability"],
        "measurement_counts": result.counts,
    }
    out_path.write_text(json.dumps(beat, indent=2))
    print(f"  Saved:      {out_path.name}")

    return True


def main():
    parser = argparse.ArgumentParser(description="AIOS Quantum Integration Test")
    parser.add_argument("--live-ionq", action="store_true", help="Run live IonQ test")
    parser.add_argument("--live-qbraid", action="store_true", help="Run live qBraid test")
    parser.add_argument("--live-all", action="store_true", help="Run all live tests")
    args = parser.parse_args()

    print("╔══════════════════════════════════════════════════════════╗")
    print("║     AIOS Quantum — Multi-Provider Integration Test      ║")
    print("╚══════════════════════════════════════════════════════════╝")

    results = {}

    # Offline tests (always run)
    results["transpilation"] = test_transpilation()
    results["local_sim"] = test_local_simulation()
    results["ionq_structure"] = test_ionq_provider_structure()
    results["qbraid_structure"] = test_qbraid_provider_structure()
    results["failover"] = test_failover_chain()

    # Live tests (only with flags)
    if args.live_ionq or args.live_all:
        results["live_ionq"] = test_live_ionq()
    if args.live_qbraid or args.live_all:
        results["live_qbraid"] = test_live_qbraid()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for test, passed in results.items():
        icon = "✓" if passed else "✗"
        print(f"  [{icon}] {test}")

    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\n  {passed}/{total} tests passed")

    # Action items
    ionq_key = bool(os.getenv("IONQ_API_KEY", ""))
    qbraid_key = bool(os.getenv("QBRAID_API_KEY", ""))

    if not ionq_key or not qbraid_key:
        print("\n" + "=" * 60)
        print("NEXT STEPS")
        print("=" * 60)

    if not ionq_key:
        print("""
  IonQ (FREE simulator, cheapest path to real quantum):
    1. Go to https://cloud.ionq.com/ and create account
    2. Settings → API Keys → Create new key
    3. Add to aios-quantum/.env:
       IONQ_API_KEY=your_key_here
    4. Run: python test_qbraid_integration.py --live-ionq
""")

    if not qbraid_key:
        print("""  qBraid (10+ QPUs, managed credits):
    1. Go to https://account.qbraid.com/ and create account
    2. Copy API Key from Plan info card (left side)
    3. Redeem access code: EHNU6626 (500 free credits)
    4. Add to aios-quantum/.env:
       QBRAID_API_KEY=your_key_here
    5. Run: python test_qbraid_integration.py --live-qbraid
""")

    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
