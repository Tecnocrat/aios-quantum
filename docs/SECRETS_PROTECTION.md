# Secrets Protection Pattern
## AIOS Quantum Security Protocol

**Created:** December 13, 2025  
**Status:** 🔴 INCIDENT RESPONSE - API KEY LEAK DETECTED  
**Protocol:** AINLP.security[MEMBRANE-HARDENING]

---

## 🚨 Incident Summary

On December 13, 2025, IBM Cloud detected a leaked Service ID API key after the repository was made public:

| Property | Value |
|----------|-------|
| **Service ID** | `cos-aios-key` |
| **APIKey UUID** | `ApiKey-091b08c9-3756-478c-aac5-b65b962c4c69` |
| **Account** | Tecnocrat (0eb4566b0a4640a3a59769e5d10a25d3) |
| **Detection Time** | December 13, 2025, 11:12 AM |
| **Exposure Source** | `docs/IBM_CLOUD_CONFIG.md` committed to public repo |

### Key Types Clarification

IBM Cloud has two types of API keys:

| Type | Purpose | Leaked? |
|------|---------|---------|
| **User API Keys** | Tied to your IBM Cloud user account | ❌ Not leaked |
| **Service ID API Keys** | Programmatic access to specific services | ✅ **LEAKED** |

**Your User API Keys (SAFE):**
- `AIOS` (ApiKey-278f22ac-...) - IBM Quantum access
- `aios-quantum-key` (ApiKey-5b5fdbe7-...) - Has "Disable on leak" enabled ✅

**Leaked Service ID Key (ROTATE IMMEDIATELY):**
- `cos-aios-key` (ApiKey-091b08c9-...) - COS Service credential

### Exposed Credentials (ROTATE IMMEDIATELY)
1. **COS API Key** - Cloud Object Storage access
2. **Cloudant API Key** - NoSQL database access
3. **Cloudant Password** - Database authentication
4. **IBM Quantum Token** - Quantum computing access

---

## 🔧 Immediate Actions Required

### Step 1: Rotate All API Keys (IBM Cloud Console)

```powershell
# Login to IBM Cloud
ibmcloud login -a https://cloud.ibm.com -u passcode

# 1. Delete compromised COS key
ibmcloud resource service-key-delete cos-aios-key -f

# 2. Create new COS key
ibmcloud resource service-key-create cos-aios-key-v2 Manager --instance-name aios-quantum-storage

# 3. Delete compromised Cloudant key
ibmcloud resource service-key-delete cloudant-aios-key -f

# 4. Create new Cloudant key
ibmcloud resource service-key-create cloudant-aios-key-v2 Manager --instance-name aios-quantum-metadata
```

### Step 2: Regenerate IBM Quantum Token

1. Go to https://quantum.ibm.com/
2. Navigate to **Account Settings** → **API Token**
3. Click **Regenerate Token**
4. Update your local `.env` file

### Step 3: Update Local Environment

After rotating keys, update your `.env` file with the new credentials:

```bash
# Get new COS credentials
ibmcloud resource service-key cos-aios-key-v2 --output json

# Get new Cloudant credentials  
ibmcloud resource service-key cloudant-aios-key-v2 --output json
```

---

## 🛡️ Secrets Protection Pattern

### The "Membrane Validator" Architecture

Following AIOS biological architecture, secrets are protected by a membrane that validates what enters/exits the codebase:

```
┌─────────────────────────────────────────────────────────────┐
│                    PUBLIC REPOSITORY                         │
│                  (GitHub - visible to all)                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ✅ ALLOWED IN REPO:                                        │
│   ├── .env.example (templates only, no real values)          │
│   ├── docs/*.md (references to env vars, not values)         │
│   ├── src/**/*.py (os.getenv() calls only)                   │
│   └── README.md (setup instructions)                         │
│                                                              │
│   ❌ BLOCKED BY MEMBRANE (.gitignore):                       │
│   ├── .env (actual credentials)                              │
│   ├── .env.local                                             │
│   ├── *.pem, *.key (certificates)                            │
│   ├── qiskit_ibm_runtime*.json (IBM tokens)                  │
│   └── Any file matching secret patterns                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                   [MEMBRANE BOUNDARY]
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    LOCAL ENVIRONMENT                         │
│               (Your machine - never committed)               │
├─────────────────────────────────────────────────────────────┤
│   .env file contains:                                        │
│   ├── IBM_QUANTUM_TOKEN=<actual_token>                       │
│   ├── COS_API_KEY=<actual_key>                               │
│   ├── CLOUDANT_API_KEY=<actual_key>                          │
│   └── CLOUDANT_PASSWORD=<actual_password>                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Prevention Patterns

### Pattern 1: Environment Variable Loading

**ALWAYS** load secrets from environment variables, never hardcode:

```python
# ✅ CORRECT - Load from environment
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("COS_API_KEY")
if not api_key:
    raise ValueError("COS_API_KEY environment variable is required")
```

```python
# ❌ WRONG - Hardcoded secret
api_key = "Gp4CuMx_1Yf5T9riqivzpA84pXIdo-vzOrd9J536ZhPo"  # NEVER DO THIS
```

### Pattern 2: Template Files

Create `.env.example` with placeholders:

```bash
# .env.example - SAFE TO COMMIT
IBM_QUANTUM_TOKEN=your_token_here
COS_API_KEY=your_cos_api_key_here
CLOUDANT_API_KEY=your_cloudant_api_key_here
```

### Pattern 3: Documentation References

In documentation, reference environment variables, don't show values:

```markdown
# ✅ CORRECT
| **API Key** | `<see .env: COS_API_KEY>` |

# ❌ WRONG  
| **API Key** | `Gp4CuMx_1Yf5T9riqivzpA84pXIdo-vzOrd9J536ZhPo` |
```

---

## 🔍 Pre-Commit Secret Scanning

### Git Pre-Commit Hook

Create `.githooks/pre-commit`:

```bash
#!/bin/bash
# Secret detection pre-commit hook

# Patterns that indicate secrets
PATTERNS=(
    '[a-zA-Z0-9_-]{40,}'           # Long API keys
    'password\s*=\s*["\'][^"\']+["\']'  # Passwords
    'api_key\s*=\s*["\'][^"\']+["\']'   # API keys
    'token\s*=\s*["\'][^"\']+["\']'     # Tokens
    'secret\s*=\s*["\'][^"\']+["\']'    # Secrets
)

# Files to check (staged files)
FILES=$(git diff --cached --name-only --diff-filter=ACM)

# Known safe patterns to ignore
SAFE_PATTERNS=(
    'your_.*_here'
    '<.*>'
    'placeholder'
    'example'
)

found_secrets=0

for file in $FILES; do
    # Skip binary files and .env.example
    if [[ "$file" == *.env.example ]] || [[ "$file" == *.png ]] || [[ "$file" == *.jpg ]]; then
        continue
    fi
    
    for pattern in "${PATTERNS[@]}"; do
        matches=$(grep -E "$pattern" "$file" 2>/dev/null || true)
        if [ -n "$matches" ]; then
            # Check if it's a safe pattern
            is_safe=0
            for safe in "${SAFE_PATTERNS[@]}"; do
                if echo "$matches" | grep -qE "$safe"; then
                    is_safe=1
                    break
                fi
            done
            
            if [ $is_safe -eq 0 ]; then
                echo "⚠️  POTENTIAL SECRET DETECTED in $file:"
                echo "$matches"
                found_secrets=1
            fi
        fi
    done
done

if [ $found_secrets -eq 1 ]; then
    echo ""
    echo "❌ Commit blocked: Potential secrets detected!"
    echo "   Review the above files and remove any hardcoded credentials."
    echo "   Use environment variables instead (see docs/SECRETS_PROTECTION.md)"
    exit 1
fi

echo "✅ No secrets detected"
exit 0
```

### Enable the Hook

```powershell
# Configure git to use the hooks directory
git config core.hooksPath .githooks

# Make hook executable (on Unix systems)
chmod +x .githooks/pre-commit
```

---

## 📁 Updated .gitignore

Ensure your `.gitignore` includes:

```gitignore
# ===== SECRETS PROTECTION =====

# Environment files (contain API keys)
.env
.env.local
.env.*.local
.env.production
.env.development

# IBM Cloud credentials
.bluemix/
qiskit_ibm_runtime*.json
ibmcloud_credentials.json

# Certificates and keys
*.pem
*.key
*.p12
*.pfx
*.cert

# AWS credentials (if ever used)
.aws/
credentials

# Google Cloud credentials
*.json.key
service-account*.json

# SSH keys
id_rsa
id_ed25519
*.ppk

# Secrets directories
secrets/
.secrets/
private/
```

---

## 🔄 Git History Cleanup (Optional but Recommended)

The leaked secret exists in git history. For complete removal:

### Option A: BFG Repo Cleaner (Recommended)

```powershell
# Install BFG
# Download from https://rtyley.github.io/bfg-repo-cleaner/

# Create a file with secrets to remove
echo "Gp4CuMx_1Yf5T9riqivzpA84pXIdo-vzOrd9J536ZhPo" > secrets-to-remove.txt
echo "4968opk2dXdmpjH-tRV0Vatsik5e-45_Kqgv3e0q-Jf4" >> secrets-to-remove.txt
echo "Th5QSXWUZ-QMgaUw8ZJuTPEtQS270jlZSs_pkkggToCp" >> secrets-to-remove.txt
echo "a125cd70d1dbdc6c1a5e1dcab90bedd0" >> secrets-to-remove.txt

# Run BFG
java -jar bfg.jar --replace-text secrets-to-remove.txt aios-quantum.git

# Clean up
cd aios-quantum.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push (WARNING: rewrites history)
git push --force
```

### Option B: Accept History Exposure

Since keys will be rotated anyway, history cleanup is optional. The rotated keys will be invalid.

---

## ✅ Security Checklist

### Immediate (Do Now)
- [ ] Rotate COS API key in IBM Cloud Console
- [ ] Rotate Cloudant API key in IBM Cloud Console
- [ ] Regenerate IBM Quantum token
- [ ] Update local `.env` with new credentials
- [ ] Verify services still work with new keys

### Short-term (This Week)
- [ ] Enable git pre-commit hook for secret scanning
- [ ] Review all documentation for exposed credentials
- [ ] Review git history (optional: clean with BFG)
- [ ] Enable GitHub secret scanning if available

### Ongoing
- [ ] Never commit files named `.env` (only `.env.example`)
- [ ] Always use `os.getenv()` for credentials in code
- [ ] Reference env vars in docs, never actual values
- [ ] Run secret scan before any commit

---

## 📚 Related Documents

- [IBM_CLOUD_CONFIG.md](./IBM_CLOUD_CONFIG.md) - Configuration reference (sanitized)
- [.env.example](../.env.example) - Environment template
- [AINLP_EMERGENT_PATTERNS.md](./AINLP_EMERGENT_PATTERNS.md) - Security patterns

---

## 🔗 External Resources

- [IBM Cloud API Key Management](https://cloud.ibm.com/docs/account?topic=account-manapikey)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [BFG Repo Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)
- [git-secrets](https://github.com/awslabs/git-secrets)

---

*AINLP.security[MEMBRANE-HARDENING] - Biological immune system for secrets protection*
