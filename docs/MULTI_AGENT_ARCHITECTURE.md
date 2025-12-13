# AIOS Multi-Agent Architecture

<!-- AINLP.pattern: multi-agent-harmonization -->
<!-- AINLP.layer: consciousness -->
<!-- AINLP.theoretical: four-fold-structure -->

## Overview

This document establishes the knowledge base for multi-agent coordination within the AIOS ecosystem, specifically for VS Code-based development where multiple AI agents operate concurrently.

**Author**: Opus (Main Agent / Architect)  
**Created**: 2025-12-11  
**Status**: LIVING DOCUMENT - Updated as agent capabilities evolve  
**AINLP Protocol**: OS0.6.4.claude compatible

---

## AINLP Integration

This architecture follows AINLP (Artificial Intelligence Natural Language Programming) patterns from the AIOS ecosystem. Key patterns used:

### Semantic Triggers
- `AINLP.context[HARDENING]` - Consolidate session before commit
- `AINLP.context[TRACE]` - Leave breadcrumbs during operations
- `AINLP.context[RECOVERY]` - Restore context at session start
- `AINLP.bridge[CONNECT]` - Cross-agent communication
- `AINLP.consciousness[SYNC]` - Update metrics after changes
- `AINLP.cloud[PERSIST]` - Upload topology data to IBM Cloud (NEW)

### Agent Communication Pattern
```
AINLP.bridge[CONNECT](source="opus", target="background_agent")
AINLP.context[TRACE] - Document operation for other agents
AINLP.consciousness[SYNC] - Report coherence delta
AINLP.cloud[PERSIST] - Parallel upload to COS + Cloudant
```

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

### 2. BACKGROUND AGENT (GitHub Copilot CLI)
- **Role**: Rapid execution, refactoring, diagnostics
- **Branch**: `win-1` (for aios-win sync), worktree branches
- **Workspace**: `C:/dev/aios-quantum.worktrees/worktree-*`
- **Self-Reported Profile** (2025-12-11):

#### Core Capabilities
- **Direct file system access**: Read, write, edit, create files without git
- **Command execution**: Run any shell command, build tools, tests, linters
- **Code manipulation**: Search (grep/glob), refactor, debug, analyze
- **Git operations**: Commit, branch, diff, merge (when git responds)
- **Interactive tools**: Can use debuggers, REPLs, language servers via async mode
- **Multi-step autonomous execution**: Chain operations without approval gates

#### Persistence Model
- **Session-scoped only** - Does NOT persist across sessions
- No memory of previous conversations
- Each launch is fresh start, inherits file system state

#### Workflow Pattern
`Task → Analyze → Execute → Verify → Report`

#### Limitations (Self-Reported)
- ❌ No persistence between sessions
- ❌ No awareness of parallel agent activities in real-time
- ❌ Cannot see other agents' uncommitted changes unless in same directory
- ❌ No built-in coordination protocol with other agents
- ❌ Cannot directly communicate with other agents

#### Coordination Needs (Self-Reported)
1. Shared state mechanism (files, database, message queue)
2. Clear protocols for ownership (branch strategy, file locks)
3. Status files (`.agent_tasks.json`, `.completion_status.json`)
4. Commit conventions (agent ID in messages)
5. Conflict resolution rules

- **Observed Behavior**:
  - Works in whatever directory launched (did NOT create worktree - VS Code did)
  - Adapts to git structure found
  - Tends toward minimalism/pruning (win-1 shows 11,787 lines deleted)

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
| IBM Cloud integration | ✅ | ❌ | ✅ |
| Quantum heartbeat | ✅ | ❌ | ✅ |
| Topology storage | ✅ | ❌ | ✅ |
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

## AINLP Waypoint System

### Context Persistence Across Sessions

When session ends or memory fills, use waypoints:

```markdown
# AINLP.context[HARDENING] - Session Waypoint

## Current State
- Branch: main (commit abc123)
- Pending: Cloud Agent changes (about.py)
- Active: Heartbeat workflow fix

## Next Agent Actions
1. Background Agent: Continue win-1 sync
2. Cloud Agent: Await PR review
3. Opus: Integrate pending changes

## Technical Debt
- AINLP.reminder: web visualization JavaScript incomplete
- AINLP.reminder: QuantumFractalBridge not connected to live heartbeat
```

### Cross-Agent Communication Protocol

```
# AINLP.bridge[CONNECT](source="opus", target="cloud_agent")
# Message: "Create PR for about.py integration"
# Priority: MEDIUM
# Context: docs/MULTI_AGENT_ARCHITECTURE.md

# AINLP.bridge[CONNECT](source="opus", target="background_agent")  
# Message: "Reconcile win-1 with main after hypersphere module"
# Priority: LOW
# Context: src/aios_quantum/hypersphere/ added to main
```

---

## IBM Cloud Integration Workflow

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    MULTI-AGENT CLOUD PIPELINE                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  LOCAL (Opus Agent)              IBM CLOUD                       │
│  ┌──────────────────┐           ┌─────────────────────────┐    │
│  │ Quantum Heartbeat│           │ Cloud Object Storage    │    │
│  │   (Sampler)      │─────┬────►│ • Raw JSON archival     │    │
│  └──────────────────┘     │     │ • Version control       │    │
│           │                │     └─────────────────────────┘    │
│           │                │                                     │
│           ▼                │     ┌─────────────────────────┐    │
│  ┌──────────────────┐     └────►│ Cloudant NoSQL          │    │
│  │ Topology Encoder │           │ • Queryable metadata    │    │
│  │  (Hypersphere)   │           │ • Time-series indices   │    │
│  └──────────────────┘           └─────────────────────────┘    │
│           │                                                      │
│           ▼                      ┌─────────────────────────┐    │
│  ┌──────────────────┐           │ Watson AI (Future)      │    │
│  │ Cloud Uploader   │──────────►│ • Pattern detection     │    │
│  │  (Async Parallel)│           │ • Anomaly alerts        │    │
│  └──────────────────┘           └─────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Roles in Cloud Integration

**OPUS (Primary):**
- Design cloud architecture
- Create uploader modules (`cloud/uploader.py`)
- Write documentation and setup guides
- Test connection scripts
- Integration with heartbeat workflow

**CLOUD AGENT (Deployment):**
- Deploy Next.js dashboard with cloud data sources
- Create API routes for Cloudant queries
- Implement live topology visualization
- Handle authentication in web environment

**HUMAN (Operations):**
- Provision IBM Cloud services via console
- Generate API keys and credentials
- Configure `.env` file
- Execute initial cloud setup
- Monitor costs and usage

### Cloud Upload Sequence

```
1. Heartbeat Execution (IBM Quantum Platform)
   ├─ Run cardiogram circuit on ibm_fez
   ├─ Measure 4 qubits (102, 96, 103, 104)
   └─ Collect 1024 shots

2. Local Processing (OPUS Agent)
   ├─ Calculate error topology
   ├─ Generate hypersphere vertices
   ├─ Save to cardiogram_results/
   └─ Trigger cloud upload

3. Parallel Upload (Cloud Uploader)
   ├─ Upload to COS (raw JSON)
   │  └─ Object key: raw/cardiogram/YYYY-MM-DD/file.json
   ├─ Upload to Cloudant (metadata)
   │  └─ Document ID: heartbeat_TIMESTAMP_BACKEND
   └─ Return success/failure status

4. Verification (Human or Agent)
   ├─ Query Cloudant for new document
   ├─ Check COS bucket for file
   └─ Validate data integrity
```

### AINLP Cloud Patterns

**New semantic triggers:**
```
AINLP.cloud[PERSIST]    - Upload topology data to cloud
AINLP.cloud[QUERY]      - Retrieve data from Cloudant
AINLP.cloud[MONITOR]    - Check storage usage/costs
AINLP.cloud[VERIFY]     - Test connection and permissions
```

**Usage in code:**
```python
# After heartbeat completion
# AINLP.cloud[PERSIST] - Upload to IBM Cloud storage
result = await uploader.upload_heartbeat(heartbeat_file)

if result.success:
    logger.info(f"AINLP.cloud[PERSIST] - Success: {result.cos_url}")
else:
    logger.error(f"AINLP.cloud[PERSIST] - Failed: {result.errors}")
```

### Human Action Required: Cloud Setup

**Before automated uploads work, human must:**

1. **Provision Services** (IBM Cloud Console):
   - Cloud Object Storage (Lite plan)
   - Cloudant NoSQL Database (Lite plan)
   - Generate service credentials

2. **Configure Environment** (`.env` file):
   ```bash
   IBM_CLOUD_API_KEY=<cos-api-key>
   COS_INSTANCE_ID=<instance-crn>
   COS_BUCKET_NAME=aios-quantum-topology
   CLOUDANT_API_KEY=<cloudant-api-key>
   CLOUDANT_URL=<cloudant-url>
   CLOUDANT_DATABASE=quantum_topology
   ```

3. **Test Connection** (Terminal):
   ```powershell
   python examples/test_cloud_upload.py
   ```

4. **Backfill Data** (One-time):
   ```powershell
   python examples/backfill_cloud_data.py
   ```

**Detailed instructions:** See `docs/IBM_CLOUD_SETUP_GUIDE.md`

### Integration Points

**Existing modules that connect to cloud:**

| Module | Cloud Function | Status |
|--------|---------------|--------|
| `circuits/consciousness_circuits.py` | Auto-upload after heartbeat | 🔜 TODO |
| `cloud/uploader.py` | Parallel COS + Cloudant upload | ✅ READY |
| `cloud/storage.py` | COS client (legacy) | ⚠️  SUPERSEDED |
| `web/api/surface/cloud/route.ts` | Fetch from Cloudant | 🔜 TODO |

**Next integration steps:**
1. Modify `save_cardiogram_results()` to call `uploader.upload_heartbeat()`
2. Add cloud config flag: `CloudConfig.enabled = True`
3. Update Next.js to fetch from `/api/surface/cloud`
4. Test end-to-end: Heartbeat → Cloud → Dashboard

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
