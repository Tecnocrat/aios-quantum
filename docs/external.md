# External Dependencies

## AIOS (Read-Only Submodule)

The main AIOS repository is included as a **read-only** Git submodule for extraction and ingestion purposes.

**Location:** `external/aios/`

### Purpose

- Extract shared utilities, models, and configurations from AIOS
- Ingest data structures and interfaces for quantum integration
- Reference implementation patterns and coding standards
- **NOT for modification** - changes should be made in the main AIOS repository

### Usage

```bash
# Initial clone with submodules
git clone --recurse-submodules https://github.com/Tecnocrat/aios-quantum.git

# If already cloned, initialize submodules
git submodule update --init --recursive

# Update to latest AIOS main branch
git submodule update --remote external/aios
```

### Guidelines

1. **Read-Only**: Do not modify files in `external/aios/`
2. **Updates**: Periodically sync with upstream using `git submodule update --remote`
3. **Imports**: Import from external/aios as needed for integration
4. **Changes**: Any required changes to AIOS should be made via PR to the main repository

### Integration Points

The quantum module integrates with AIOS through:

- Shared configuration patterns
- Common data structures
- Agent communication interfaces
- Memory and context management

See `src/aios_quantum/integration/` for quantum-AIOS bridge implementations.
