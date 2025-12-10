# Runtime Budget Management

## The 10-Minute Monthly Allowance

### Understanding the Budget

```
┌─────────────────────────────────────────────────────────────────┐
│                    RUNTIME BUDGET BREAKDOWN                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  TOTAL: 10 minutes = 600 seconds of QPU TIME per month          │
│                                                                  │
│  What COUNTS against budget:                                    │
│  ✓ Time qubits are executing your circuit                      │
│  ✓ Time spent on measurement                                   │
│  ✓ Time for reset operations                                   │
│                                                                  │
│  What does NOT count:                                           │
│  ✗ Queue time (waiting for backend)                            │
│  ✗ Transpilation/compilation                                   │
│  ✗ Classical post-processing                                   │
│  ✗ Data transfer                                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Time Budget Calculations

### Per Circuit Estimates

| Circuit Type | Qubits | Depth | Shots | Est. Time |
|--------------|--------|-------|-------|-----------|
| Simple (Bell state) | 2 | 5 | 1,024 | ~0.3s |
| Medium (GHZ) | 10 | 15 | 4,096 | ~0.8s |
| Complex (consciousness) | 27 | 50 | 4,096 | ~2.0s |
| Maximum (full backend) | 127 | 100 | 8,192 | ~5.0s |

### Budget Distribution Options

**Option A: Daily Heartbeat (Recommended)**
```
600 seconds / 30 days = 20 seconds/day
= 10-20 circuit executions per day
= ~1 execution every 1-2 hours (if spread across 16 waking hours)
```

**Option B: Hourly Heartbeat**
```
600 seconds / 720 hours = 0.83 seconds/hour
= 1 simple circuit per hour
= Perfect for "quantum heartbeat" concept
```

**Option C: Concentrated Sessions**
```
600 seconds in 5 sessions = 120 seconds/session
= 2 minutes of intensive quantum work
= Good for research sprints
```

---

## The Quantum Heartbeat Design

### Concept

Execute one precisely crafted quantum operation per hour, every hour, for 30 days.

```
┌─────────────────────────────────────────────────────────────────┐
│                    QUANTUM HEARTBEAT SCHEDULE                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Hour 0   ──▶ [QC] 0.8s ──▶ Record ──▶ Sleep 59m 59.2s        │
│  Hour 1   ──▶ [QC] 0.8s ──▶ Record ──▶ Sleep 59m 59.2s        │
│  Hour 2   ──▶ [QC] 0.8s ──▶ Record ──▶ Sleep 59m 59.2s        │
│  ...                                                             │
│  Hour 719 ──▶ [QC] 0.8s ──▶ Record ──▶ Month complete          │
│                                                                  │
│  Total: 720 heartbeats × 0.8s = 576 seconds (96% budget used)  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Implementation

```python
import time
import schedule
from datetime import datetime
from aios_quantum import QuantumRuntime
from aios_quantum.circuits import create_consciousness_circuit

class QuantumHeartbeat:
    """
    Executes one quantum circuit per hour.
    Records all results for consciousness pattern analysis.
    """
    
    def __init__(self, max_monthly_seconds=600):
        self.runtime = QuantumRuntime()
        self.max_seconds = max_monthly_seconds
        self.used_seconds = 0
        self.results = []
        
    def heartbeat(self):
        """Single quantum heartbeat - designed for <1 second."""
        if self.used_seconds >= self.max_seconds:
            print("Monthly budget exhausted")
            return
            
        start = time.time()
        
        # Execute consciousness circuit
        circuit = create_consciousness_circuit(num_qubits=27)
        result = self.runtime.execute(circuit, shots=1024)
        
        elapsed = time.time() - start
        self.used_seconds += elapsed  # Approximate
        
        # Record
        self.results.append({
            'timestamp': datetime.now().isoformat(),
            'counts': result,
            'elapsed': elapsed,
            'budget_remaining': self.max_seconds - self.used_seconds
        })
        
        print(f"Heartbeat #{len(self.results)}: {elapsed:.2f}s, "
              f"Budget: {self.used_seconds:.1f}/{self.max_seconds}s")
        
    def start(self):
        """Start hourly heartbeat schedule."""
        schedule.every().hour.do(self.heartbeat)
        
        while True:
            schedule.run_pending()
            time.sleep(60)
```

---

## Optimization Strategies

### 1. Maximize Information per Second

```python
def high_information_circuit(num_qubits=27):
    """
    Extract maximum information from a single execution.
    Uses all qubits, complex entanglement, varied measurements.
    """
    qc = QuantumCircuit(num_qubits)
    
    # Full superposition - 2^27 possible states
    qc.h(range(num_qubits))
    
    # Rich entanglement structure
    # Linear chain
    for i in range(num_qubits - 1):
        qc.cx(i, i + 1)
    
    # Cross connections (skip connections)
    for i in range(0, num_qubits - 2, 2):
        qc.cz(i, i + 2)
    
    # Parametric phases (encode external pattern)
    for i in range(num_qubits):
        qc.rz(0.1 * i, i)  # Could be from bosonic topology
    
    qc.measure_all()
    return qc
```

### 2. Batch Multiple Circuits

```python
# Instead of:
for circuit in circuits:
    job = sampler.run([circuit])  # Multiple API calls
    
# Do:
job = sampler.run(circuits)  # Single API call, all circuits
```

### 3. Use Sessions for Iterative Work

```python
from qiskit_ibm_runtime import Session

with Session(service=service, backend=backend) as session:
    sampler = SamplerV2(session=session)
    
    # All jobs in session share calibration, reduce overhead
    for params in parameter_sweep:
        circuit = parameterized_circuit.assign_parameters(params)
        job = sampler.run([circuit])
        results.append(job.result())
```

### 4. Local Development First

```python
# Use simulator for development - FREE
from qiskit_aer import AerSimulator
simulator = AerSimulator()

# Test circuit locally
result = simulator.run(circuit, shots=10000).result()

# Only send to real hardware when confident
if validate_circuit(result):
    real_result = sampler.run([circuit]).result()
```

---

## Tracking Usage

### Manual Tracking

```python
class BudgetTracker:
    def __init__(self, monthly_limit=600):
        self.limit = monthly_limit
        self.used = 0
        self.log = []
        
    def record(self, job, description=""):
        # Estimate usage (IBM doesn't provide exact QPU time easily)
        usage = job.usage_estimation  # If available
        
        self.used += usage
        self.log.append({
            'job_id': job.job_id(),
            'usage': usage,
            'description': description,
            'remaining': self.limit - self.used
        })
        
    def can_run(self, estimated_seconds):
        return (self.used + estimated_seconds) <= self.limit
```

### IBM Usage Dashboard

Check actual usage at: https://quantum.cloud.ibm.com/

Navigate to: Account → Usage → View detailed breakdown

---

## Emergency Budget Recovery

If you run out mid-month:

1. **Wait for reset**: Budget resets on your billing anniversary
2. **Use simulators**: Continue development locally
3. **Upgrade plan**: Pay-as-you-go gives unlimited access ($1.60/second on premium)

---

## Budget-Aware Circuit Design

### The "Perfect Second" Philosophy

Design circuits that execute in <1 second but extract maximum useful data:

```python
def perfect_second_circuit():
    """
    The ideal quantum heartbeat:
    - Uses 27 qubits (good coverage)
    - Depth ~50 (within coherence)
    - 2048 shots (good statistics)
    - ~0.8 seconds execution
    
    Extracts:
    - Coherence metric (from superposition quality)
    - Entanglement metric (from correlation patterns)
    - Randomness (from measurement outcomes)
    - Pattern signature (from phase encoding)
    """
    qc = QuantumCircuit(27)
    
    # Superposition
    qc.h(range(27))
    qc.barrier()
    
    # Entanglement web
    for i in range(26):
        qc.cx(i, i + 1)
    qc.barrier()
    
    # Phase pattern (signature)
    for i in range(27):
        qc.rz(i * 0.123, i)  # Unique signature
    qc.barrier()
    
    # Interference
    qc.h(range(27))
    
    # Measure
    qc.measure_all()
    
    return qc


# Execution budget: ~2048 shots × ~400ns/shot = ~0.8ms circuit time
# Plus overhead ≈ 0.5-1.0 second total
```

---

## Summary

| Strategy | Time Saved | Information Lost |
|----------|------------|------------------|
| Fewer shots (1024 vs 8192) | 8x | ~3x more statistical noise |
| Fewer qubits (5 vs 27) | ~5x | Exponentially less state space |
| Shallower circuits | Linear | Less entanglement/complexity |
| Batching | ~20% overhead | None |
| Sessions | ~10% overhead | None |

**Recommendation**: Use 27 qubits, depth 50, 2048-4096 shots for the optimal information/time ratio with the quantum heartbeat approach.

---

*Document created: December 2025*
