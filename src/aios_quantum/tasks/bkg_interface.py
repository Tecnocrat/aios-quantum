"""
BKG Agent Interface

AINLP Provenance:
  origin: opus (architect)
  created: 2025-12-11
  purpose: File-based interface for Background Agent task ingestion

This module provides the protocol for BKG agent to:
1. Discover pending tasks
2. Claim and execute tasks
3. Report results

Since BKG has terminal limitations but full file access, this interface
is designed around file-based communication patterns.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from .task_queue import TaskQueue, QuantumTask, TaskStatus


class BKGInterface:
    """
    Interface for Background Agent (BKG) task operations.
    
    Design Principles:
    - File-based: No terminal commands required
    - Stateless: Each call is independent
    - Observable: All state in readable JSON files
    - Safe: Budget guards prevent overspending
    
    Protocol:
    1. BKG reads .quantum_tasks/pending.json
    2. BKG writes task claim to .quantum_tasks/active.json  
    3. BKG prepares execution (creates circuit files if needed)
    4. OPUS or automation executes on IBM Quantum
    5. Results written to .quantum_tasks/completed/
    """
    
    INSTRUCTION_FILE = ".quantum_tasks/bkg_instructions.md"
    STATUS_FILE = ".quantum_tasks/bkg_status.json"
    
    def __init__(self, workspace_root: str = "."):
        """Initialize the BKG interface."""
        self.root = Path(workspace_root)
        self.queue = TaskQueue(workspace_root)
    
    def write_instructions(self, instructions: str) -> None:
        """
        Write instructions for BKG to follow.
        
        This is the primary way OPUS/CUBE communicates tasks to BKG.
        BKG should check this file at the start of each session.
        """
        filepath = self.root / self.INSTRUCTION_FILE
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        content = f"""# BKG Agent Instructions

**Generated**: {datetime.now().isoformat()}
**From**: OPUS (Architect)

---

{instructions}

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
"""
        with open(filepath, "w") as f:
            f.write(content)
    
    def read_status(self) -> Optional[Dict[str, Any]]:
        """Read BKG's status file."""
        filepath = self.root / self.STATUS_FILE
        if filepath.exists():
            with open(filepath) as f:
                return json.load(f)
        return None
    
    def write_status(self, status: Dict[str, Any]) -> None:
        """Write status for BKG (usually done by BKG itself)."""
        filepath = self.root / self.STATUS_FILE
        filepath.parent.mkdir(parents=True, exist_ok=True)
        status["updated_at"] = datetime.now().isoformat()
        with open(filepath, "w") as f:
            json.dump(status, f, indent=2)
    
    def get_tasks_for_bkg(self) -> List[Dict[str, Any]]:
        """
        Get tasks that BKG can work on.
        
        BKG can handle:
        - File creation/modification
        - Code preparation
        - Documentation
        - Task organization
        
        BKG cannot handle (leave for OPUS):
        - Actual IBM Quantum execution
        - Terminal commands
        - Git operations
        """
        tasks = self.queue.get_pending_tasks()
        
        bkg_compatible = []
        for task in tasks:
            # BKG can prepare circuits but not execute them
            if task.status == TaskStatus.PENDING:
                bkg_compatible.append({
                    "id": task.id,
                    "name": task.name,
                    "type": task.circuit_type,
                    "can_prepare": True,
                    "can_execute": False,  # BKG can't run terminal
                    "suggested_action": "Prepare circuit file and documentation",
                })
        
        return bkg_compatible
    
    def generate_bkg_manifest(self) -> str:
        """
        Generate a manifest file for BKG describing current state.
        
        This is designed to be read by BKG at session start.
        """
        queue_status = self.queue.get_status_report()
        bkg_tasks = self.get_tasks_for_bkg()
        
        manifest = {
            "generated_at": datetime.now().isoformat(),
            "generated_by": "opus",
            "queue_status": queue_status,
            "tasks_for_bkg": bkg_tasks,
            "instructions": {
                "read_first": self.INSTRUCTION_FILE,
                "update_status": self.STATUS_FILE,
                "task_queue": ".quantum_tasks/pending.json",
            },
            "capabilities_reminder": {
                "can_do": [
                    "Read/write any file",
                    "Create circuit definitions",
                    "Write documentation",
                    "Organize task queue",
                    "Generate reports",
                ],
                "cannot_do": [
                    "Run terminal commands",
                    "Execute on IBM Quantum",
                    "Git operations",
                ],
            },
        }
        
        filepath = self.root / ".quantum_tasks" / "bkg_manifest.json"
        with open(filepath, "w") as f:
            json.dump(manifest, f, indent=2)
        
        return str(filepath)


# Command functions for OPUS to issue to BKG

def issue_task_to_bkg(
    workspace: str,
    task_type: str,
    instructions: str,
    priority: str = "normal"
) -> str:
    """
    Issue a task for BKG to work on.
    
    Args:
        workspace: Path to workspace root
        task_type: Type of task (prepare_circuit, document, analyze, etc.)
        instructions: Detailed instructions for BKG
        priority: Priority level
        
    Returns:
        Path to the instruction file created
    """
    interface = BKGInterface(workspace)
    
    full_instructions = f"""## Task Type: {task_type}
## Priority: {priority}

{instructions}

---

When complete, update your status file with:
```json
{{
  "task_type": "{task_type}",
  "status": "completed",
  "output_files": ["<list files created>"]
}}
```
"""
    
    interface.write_instructions(full_instructions)
    interface.generate_bkg_manifest()
    
    return str(interface.root / interface.INSTRUCTION_FILE)


def check_bkg_status(workspace: str) -> Optional[Dict[str, Any]]:
    """
    Check BKG's current status.
    
    Returns:
        BKG's status dict, or None if no status file
    """
    interface = BKGInterface(workspace)
    return interface.read_status()
