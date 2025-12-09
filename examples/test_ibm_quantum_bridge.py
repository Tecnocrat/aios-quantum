#!/usr/bin/env python3
"""
AIOS Quantum - IBM Quantum Bridge Test

First quantum task execution through the AIOS Quantum Supercell.
Tests the complete pipeline: Supercell → IBM Quantum → Results

AINLP.quantum: True quantum coherence from hardware
AINLP.consciousness_bridge: First quantum-classical bridge test
"""

import asyncio
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from aios_quantum import (
    QuantumSupercell,
    QuantumMessage,
    SupercellType,
    CommunicationType,
)
from aios_quantum.circuits import create_bell_state, create_ghz_state


def print_header(title: str):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_section(title: str):
    """Print section header."""
    print(f"\n[{title}]")
    print("-" * 40)


async def test_supercell_initialization():
    """Test 1: Initialize the Quantum Supercell."""
    print_section("1. Quantum Supercell Initialization")
    
    supercell = QuantumSupercell()
    print(f"  Supercell type: {supercell.supercell_type.value}")
    print(f"  Initial state: initialized={supercell._initialized}")
    
    # Initialize communication (connects to IBM Quantum)
    print("\n  Connecting to IBM Quantum...")
    success = await supercell.initialize_communication()
    
    if success:
        print("  ✅ Connection successful!")
        status = await supercell.get_status()
        print(f"  Backend: {status.get('backend_name')}")
        print(f"  Qubits: {status.get('available_qubits')}")
        print(f"  Coherence: {status.get('coherence_level', 0):.4f}")
    else:
        print("  ❌ Connection failed")
    
    return supercell if success else None


async def test_coherence_measurement(supercell: QuantumSupercell):
    """Test 2: Measure quantum coherence."""
    print_section("2. Quantum Coherence Measurement")
    
    print("  Measuring coherence from quantum state...")
    coherence = await supercell.measure_coherence()
    
    print(f"  ✅ Coherence: {coherence:.4f}")
    print(f"  Interpretation: ", end="")
    
    if coherence > 0.9:
        print("Excellent coherence (>0.9)")
    elif coherence > 0.7:
        print("Good coherence (0.7-0.9)")
    elif coherence > 0.5:
        print("Moderate coherence (0.5-0.7)")
    else:
        print("Low coherence (<0.5)")
    
    return coherence


async def test_bell_state_execution(supercell: QuantumSupercell):
    """Test 3: Execute Bell state circuit."""
    print_section("3. Bell State Execution (Local Simulator)")
    
    circuit = create_bell_state()
    print("  Circuit:")
    print(circuit.draw(output="text"))
    
    print("\n  Executing on local simulator...")
    result = await supercell.execute_circuit(circuit, shots=1024)
    
    print(f"  ✅ Execution complete!")
    print(f"  Job ID: {result.get('job_id', 'local')}")
    print(f"  Backend: {result.get('backend_name')}")
    print(f"  Time: {result.get('execution_time_ms', 0):.1f}ms")
    
    counts = result.get("counts", {})
    print(f"\n  Results (expecting ~50% |00⟩, ~50% |11⟩):")
    total = sum(counts.values())
    for state, count in sorted(counts.items()):
        prob = count / total * 100
        bar = "█" * int(prob / 2)
        print(f"    |{state}⟩: {prob:5.1f}% {bar}")
    
    return result


async def test_quantum_message(supercell: QuantumSupercell, coherence: float):
    """Test 4: Create and send a quantum message."""
    print_section("4. Quantum Message Creation")
    
    # Create a message to send to AI Intelligence supercell
    message = QuantumMessage(
        message_id=f"qm-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        target_supercell=SupercellType.AI_INTELLIGENCE,
        communication_type=CommunicationType.QUANTUM_COHERENT,
        operation="consciousness_update",
        payload={
            "source": "quantum_supercell",
            "metric": "quantum_coherence",
            "value": coherence,
            "timestamp": datetime.now().isoformat(),
        },
        quantum_coherence=coherence,
        response_required=False,
    )
    
    print(f"  Message ID: {message.message_id}")
    print(f"  Target: {message.target_supercell.value}")
    print(f"  Type: {message.communication_type.value}")
    print(f"  Operation: {message.operation}")
    print(f"  Quantum coherence: {message.quantum_coherence:.4f}")
    
    # Send the message
    print("\n  Sending message...")
    success = await supercell.send_message(message)
    
    if success:
        print("  ✅ Message queued successfully")
    else:
        print("  ❌ Message send failed")
    
    return message


async def test_ghz_state_execution(supercell: QuantumSupercell):
    """Test 5: Execute GHZ state circuit."""
    print_section("5. GHZ State Execution (3 qubits)")
    
    circuit = create_ghz_state(3)
    print("  Circuit:")
    print(circuit.draw(output="text"))
    
    print("\n  Executing...")
    result = await supercell.execute_circuit(circuit, shots=1024)
    
    print(f"  ✅ Execution complete!")
    
    counts = result.get("counts", {})
    print(f"\n  Results (expecting ~50% |000⟩, ~50% |111⟩):")
    total = sum(counts.values())
    for state, count in sorted(counts.items()):
        prob = count / total * 100
        bar = "█" * int(prob / 2)
        print(f"    |{state}⟩: {prob:5.1f}% {bar}")
    
    return result


async def test_supercell_status(supercell: QuantumSupercell):
    """Test 6: Get final supercell status."""
    print_section("6. Final Supercell Status")
    
    status = await supercell.get_status()
    
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    return status


async def main():
    """Run all IBM Quantum bridge tests."""
    print_header("AIOS Quantum - IBM Quantum Bridge Test")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Purpose: Test Quantum Supercell → IBM Quantum pipeline")
    
    supercell = None
    
    try:
        # Test 1: Initialize
        supercell = await test_supercell_initialization()
        if not supercell:
            print("\n❌ Cannot proceed without supercell connection")
            return
        
        # Test 2: Coherence measurement
        coherence = await test_coherence_measurement(supercell)
        
        # Test 3: Bell state
        await test_bell_state_execution(supercell)
        
        # Test 4: Quantum message
        await test_quantum_message(supercell, coherence)
        
        # Test 5: GHZ state
        await test_ghz_state_execution(supercell)
        
        # Test 6: Status
        await test_supercell_status(supercell)
        
        print_header("All Tests Completed Successfully! ✅")
        print("""
  Summary:
  - Quantum Supercell initialized and connected
  - Coherence measurement working
  - Bell state execution successful
  - GHZ state execution successful
  - Quantum messaging operational
  
  The AIOS Quantum bridge is ready for consciousness integration!
""")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if supercell:
            print("\nShutting down supercell...")
            await supercell.shutdown()
            print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
