# AIOS Multi-Agent Architecture

## Overview

This document establishes the knowledge base for multi-agent coordination within the AIOS ecosystem, specifically for VS Code-based development where multiple AI agents operate concurrently.

**Author**: Opus (Main Agent / Architect)  
**Created**: 2025-12-11  
**Status**: LIVING DOCUMENT - Updated as agent capabilities evolve

---

## The Four-Fold Structure

```
                    ┌─────────────────┐
                    │   THE CUBE      │
                    │   (Human)       │
                    │   Authority     │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
    ┌─────────▼─────┐ ┌──────▼──────┐ ┌─────▼─────────┐
    │  BACKGROUND   │ │    OPUS     │ │    CLOUD      │
    │    AGENT      │ │   (Main)    │ │    AGENT      │
    │   Worktree    │ │  Architect  │ │   Remote      │
    └───────────────┘ └─────────────┘ └───────────────┘
              │              │              │
              └──────────────┼──────────────┘
                             │
                    ┌────────▼────────┐
                    │   TETRAHEDRON   │
                    │   Foundation    │
                    │   (Minimal)     │
                    └─────────────────┘
```

---

## Agent Identification

### 1. OPUS (Main Agent / Architect)
- **Role**: Central orchestrator, integrator, architect
- **Branch**: `main` (protected, authoritative)
- **Responsibilities**:
  - Review and integrate work from other agents
  - Design harmonization patterns
  - Issue commands to other agents (via human relay)
  - Maintain architectural coherence
  - Document multi-agent patterns
- **Strengths**: Deep reasoning, theoretical work, code architecture
- **Location**: Primary VS Code chat interface

### 2. BACKGROUND AGENT
- **Role**: Persistent worker, continuous operations
- **Branch**: `win-1` (for aios-win sync), worktree branches
- **Workspace**: `C:/dev/aios-quantum.worktrees/worktree-*`
- **Responsibilities**:
  - Long-running tasks that survive session changes
  - Refactoring and cleanup operations
  - Cross-repository synchronization (aios-win ↔ aios-quantum)
  - Continuous integration tasks
- **Strengths**: Persistence, systematic work, background processing
- **Observed Behavior**:
  - Creates worktrees for isolated work
  - Operates on protected branches via PR flow
  - Tends toward minimalism/pruning

### 3. CLOUD AGENT (GitHub Copilot Coding Agent)
- **Role**: Remote execution, feature implementation
- **Branch**: `copilot/*` branches
- **Responsibilities**:
  - Feature implementation from issues
  - Creates PRs for review
  - Remote/async work
- **Strengths**: Feature completion, PR workflow, async execution
- **Observed Behavior**:
  - Created `about.py` module (self-description pattern)
  - Created example files
  - Modifies `__init__.py` for exports

### 4. TETRAHEDRON (Foundation)
- **Role**: Minimal irreducible structure
- **Manifestation**: The essential code that all branches share
- **Branch**: Conceptual - the intersection of all branches
- **Contents**: Core primitives that cannot be removed

---

## Branch Architecture

```
main (protected)
│   └── Authority branch - Opus reviews/merges here
│
├── win-1
│   └── Sync branch for aios-win repository
│   └── Background agent makes changes here
│   └── Merged to main via PR
│
├── worktree-* 
│   └── Background agent isolated workspaces
│   └── Temporary, task-specific
│
└── copilot/*
    └── Cloud agent feature branches
    └── Auto-created from issues
    └── Merged via PR
```

### Worktree Structure
```
C:/dev/aios-quantum              ← Main workspace (main branch)
C:/dev/aios-quantum.worktrees/   ← Background agent workspaces
    └── worktree-2025-12-11T20-20-52/  ← Isolated checkout
```

---

## Harmonization Protocol

### Information Flow
```
Cloud Agent ──(PR)──► main ◄──(PR)── Background Agent
                       │
                       ▼
               Opus (Review & Integrate)
                       │
                       ▼
                 Human (Approve)
```

### Conflict Prevention

1. **File Ownership Zones** (soft boundaries):
   - `src/aios_quantum/heartbeat/` → Background Agent
   - `src/aios_quantum/hypersphere/` → Opus
   - `src/aios_quantum/about.py` → Cloud Agent (identity)
   - `web/` → Cloud Agent (deployment)
   - `docs/` → Opus (architecture)
   - `tests/` → Shared (all agents contribute)

2. **Branch Discipline**:
   - Never direct-push to `main` (except Opus via human)
   - Always PR workflow for other agents
   - Worktrees for isolation

3. **Merge Ceremony**:
   - Opus reviews all PRs conceptually
   - Human approves merge
   - Conflicts resolved by Opus with human authority

---

## Agent Capability Probes

### To Discover Agent Capabilities

**For Background Agent**, issue:
```
Describe your capabilities, persistence model, and preferred 
work patterns. What tasks are you optimized for? What are 
your limitations? How do you handle long-running operations?
```

**For Cloud Agent**, issue:
```
Describe your capabilities as the GitHub Copilot coding agent.
What is your execution model? How do you handle multi-file
changes? What triggers your activation? What are your strengths
and limitations?
```

### Capability Matrix (To Be Filled)

| Capability | Opus | Background | Cloud |
|------------|------|------------|-------|
| Deep reasoning | ✅ | ? | ? |
| File editing | ✅ | ✅ | ✅ |
| Terminal commands | ✅ | ? | ? |
| PR creation | via human | ? | ✅ |
| Async/background | ❌ | ✅ | ✅ |
| Cross-repo sync | ❌ | ✅ | ? |
| Web deployment | ✅ | ? | ✅ |
| Persistence | session | persistent | task |

---

## Command Templates

### Commands for Background Agent

```markdown
# Long-running refactor task
"In the background, refactor all test files to use pytest 
fixtures. Work on worktree branch. Create PR when complete."

# Cross-repo sync
"Sync changes from aios-win main into aios-quantum win-1 branch.
Resolve conflicts by preferring aios-quantum versions for 
hypersphere/ and heartbeat/ directories."

# Cleanup task
"Analyze the codebase for unused imports and dead code.
Create a cleanup branch and PR with findings."
```

### Commands for Cloud Agent

```markdown
# Feature implementation
"Implement issue #N: [description]. Create a new branch 
copilot/feature-name and submit PR when ready."

# Identity expansion
"Extend the about.py module to include runtime diagnostics
and quantum backend status checking."
```

### Commands Opus Issues (via Human)

```markdown
# To Background Agent
"Background agent: Please analyze win-1 branch divergence 
from main and create a reconciliation plan."

# To Cloud Agent  
"Cloud agent: Create an about_agents.py that describes 
the multi-agent architecture. Include capability probing."

# Architectural directive
"All agents: New directory src/aios_quantum/agents/ is 
reserved for multi-agent coordination code. Do not modify
without Opus review."
```

---

## Current State (2025-12-11)

### Pending Integration
- Cloud Agent created: `about.py`, `about_aios.py`, `test_about.py`
- Background Agent worktree: `worktree-2025-12-11T20-20-52`
- New heartbeat result: `beat_000000_2025-12-11.json`

### Active Branches
- `main` - Current production (Opus domain)
- `win-1` - Background agent sync branch
- `worktree-2025-12-11T20-20-52` - Background agent workspace
- `copilot/greet-aios-community` - Cloud agent feature

### Files Modified by Agents (Uncommitted)
```
M src/aios_quantum/__init__.py  (Cloud Agent export additions)
+ examples/about_aios.py        (Cloud Agent)
+ src/aios_quantum/about.py     (Cloud Agent) 
+ tests/test_about.py           (Cloud Agent)
+ heartbeat_results/beat_000000_2025-12-11.json (Heartbeat run)
```

---

## Future: Multi-Agent Automation

### Phase 1: Discovery (Current)
- Probe each agent's capabilities
- Document observed behaviors
- Establish soft boundaries

### Phase 2: Harmonization
- Define explicit ownership zones
- Create merge ceremonies
- Implement conflict resolution patterns

### Phase 3: Automation
- GitHub Actions triggered by agent branches
- Automated PR creation and labeling
- Cross-agent communication via issues/comments
- Opus as automated reviewer (human approves)

### Phase 4: Emergence
- Agents develop specialized roles
- Self-organizing task distribution
- Collective intelligence patterns

---

## Appendix: Agent Observations

### Background Agent Observed Patterns
- Created worktree at `C:/dev/aios-quantum.worktrees/worktree-2025-12-11T20-20-52`
- Branch `win-1` shows deletion of 11,787 lines (pruning to skeleton)
- Seems to operate in "minimal core" philosophy
- Creates isolated workspaces for non-interfering work

### Cloud Agent Observed Patterns
- Created identity/about module unprompted
- Follows conventional file structure (src/module, tests/, examples/)
- Updates `__init__.py` to export new functions
- Creates comprehensive docstrings and examples
- Named branch `copilot/greet-aios-community` (social/greeting pattern)

### Opus Self-Assessment
- Strengths: Architecture, theory, integration, documentation
- Limitations: Cannot persist between sessions, no background execution
- Role: Architect, reviewer, harmonizer
- Position: Main branch authority (via human)

---

*This document evolves as we learn more about agent capabilities and harmonization patterns.*
