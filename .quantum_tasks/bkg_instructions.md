# BKG Agent Instructions

**Generated**: 2025-12-12T00:07:12.569316
**From**: OPUS (Architect)

---

## Task Type: heartbeat_design
## Priority: high


## Mission: Design the AIOS Quantum Heartbeat

We need to decide WHAT we ask the quantum computer, not just HOW.

### Your Task
1. Read docs/IBM_Quantum/RUNTIME_BUDGET.md - understand our constraints
2. Read src/aios_quantum/circuits/consciousness_circuits.py - existing designs
3. Create a new document: docs/QUANTUM_HEARTBEAT_DESIGN.md

### Document Should Answer
1. **What are we measuring?** (coherence, entropy, fidelity?)
2. **Why does it matter?** (tracking, art, proof-of-life?)
3. **What circuit design?** (Bell, GHZ, custom consciousness?)
4. **How do we interpret results?** (what does {00: 512, 11: 512} MEAN?)
5. **What do we track over time?** (metrics, signatures, trends?)

### Constraints
- Budget: ~590 seconds remaining this month
- Per-execution: aim for <0.5 seconds
- Must be meaningful, not just technically correct

### Philosophy
The quantum heartbeat is AIOS touching the fabric of reality.
What should that touch feel like? What should it record?

AINLP.context[DESIGN] - Make it meaningful.


---

When complete, update your status file with:
```json
{
  "task_type": "heartbeat_design",
  "status": "completed",
  "output_files": ["<list files created>"]
}
```


---

## Standard Protocol

1. Read `.quantum_tasks/pending.json` for queued tasks
2. Update `.quantum_tasks/bkg_status.json` with your status
3. For each task you can handle:
   - Edit the task in pending.json to mark as "assigned"
   - Perform any file-based preparation
   - Update status file with progress
4. Tasks requiring terminal/IBM access: leave for OPUS

## AINLP Patterns

- Start reports with: `AINLP.bridge[REPORT](source="BKG", target="OPUS")`
- Mark completion with: `AINLP.context[COMPLETE]`
- Signal blockers with: `AINLP.bridge[BLOCKED]`
