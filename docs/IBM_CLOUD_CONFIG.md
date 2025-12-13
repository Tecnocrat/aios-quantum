# IBM Cloud Configuration Reference
## AIOS Quantum Project

**Last Updated:** December 13, 2025  
**Status:** ✅ FULLY CONFIGURED AND TESTED

> ⚠️ **SECURITY NOTE**: All API keys and secrets have been removed from this file.
> See [SECRETS_PROTECTION.md](./SECRETS_PROTECTION.md) for the secure secrets management pattern.
> Actual credentials are stored in your local `.env` file (gitignored).

---

## Account Information

| Property | Value |
|----------|-------|
| **Account Name** | Tecnocrat |
| **Account ID** | `<see .env: IBM_CLOUD_ACCOUNT_ID>` |
| **User** | `<your IBM Cloud email>` |
| **Resource Group** | Default |

---

## IBM Cloud CLI

| Property | Value |
|----------|-------|
| **Version** | 2.40.0 |
| **Install Path** | `C:\Program Files\IBM\Cloud\bin\ibmcloud.exe` |
| **Install Date** | December 13, 2025 |
| **Config Path** | `C:\Users\<user>\.bluemix\` |

### Quick Commands
```powershell
# Check version
ibmcloud version

# Login with passcode (get from cloud.ibm.com)
ibmcloud login -a https://cloud.ibm.com -u passcode -p <PASSCODE>

# Target resource group
ibmcloud target -g Default

# List services
ibmcloud resource service-instances
```

---

## Cloud Object Storage (COS)

### Service Details
| Property | Value |
|----------|-------|
| **Service Name** | aios-quantum-storage |
| **Plan** | Lite (Free) |
| **Location** | Global |
| **Created** | December 9, 2025 |
| **Instance CRN** | `<see .env: COS_INSTANCE_ID>` |

### Credentials
| Property | Value |
|----------|-------|
| **Credential Name** | cos-aios-key |
| **Role** | Manager |
| **API Key** | `<see .env: COS_API_KEY>` |

### Buckets
| Bucket Name | Purpose | Region |
|-------------|---------|--------|
| `aios-quantum-experiments` | Raw experiment data, circuit definitions | us-east |
| `aios-quantum-results` | Processed results, analysis outputs | us-east |

### Endpoint
```
https://s3.us-east.cloud-object-storage.appdomain.cloud
```

### CLI Commands
```powershell
# List buckets
ibmcloud cos buckets

# List objects in bucket
ibmcloud cos objects --bucket aios-quantum-experiments

# Upload file
ibmcloud cos upload --bucket aios-quantum-experiments --key raw/test.json --file ./test.json
```

---

## Cloudant NoSQL Database

### Service Details
| Property | Value |
|----------|-------|
| **Service Name** | aios-quantum-metadata |
| **Plan** | Lite (Free: 1 GB, 20 reads/sec) |
| **Location** | us-south |
| **Created** | December 13, 2025 |
| **Instance GUID** | `<see IBM Cloud Console>` |

### Credentials
| Property | Value |
|----------|-------|
| **Credential Name** | cloudant-aios-key |
| **Role** | Manager |
| **API Key** | `<see .env: CLOUDANT_API_KEY>` |
| **Host** | `<see .env: CLOUDANT_HOST>` |

### URL
```
<see .env: CLOUDANT_URL>
```

### Database
| Database Name | Purpose |
|---------------|---------|
| `quantum_topology` | Heartbeat metadata, error topology, queryable indices |

### CLI Commands
```powershell
# List service keys
ibmcloud resource service-keys --instance-name aios-quantum-metadata

# Get credentials
ibmcloud resource service-key cloudant-aios-key
```

---

## IBM Quantum Computing

### Service Details
| Property | Value |
|----------|-------|
| **Service Name** | open-instance (Qiskit Runtime) |
| **Plan** | Open Plan (free tier) |
| **Location** | us-east |
| **Instance CRN** | `<see .env: IBM_QUANTUM_INSTANCE>` |

### Available Backends
| Backend | Qubits | Status |
|---------|--------|--------|
| ibm_fez | 156 | Available |
| ibm_torino | 133 | Available |
| ibm_kyiv | 156 | Available |
| ibm_sherbrooke | 127 | Available |

### Authentication Token
```
<see .env: IBM_QUANTUM_TOKEN>
```

---

## Environment Variables Template

Copy this to your `.env` file and fill in your actual credentials:

```bash
# ===== IBM Quantum Configuration =====
# Get from: https://quantum.cloud.ibm.com/ → Account settings → API token
IBM_QUANTUM_TOKEN=your_ibm_quantum_token_here
IBM_QUANTUM_INSTANCE=crn:v1:bluemix:public:quantum-computing:us-east:a/<account_id>:<instance_id>::
IBM_QUANTUM_CHANNEL=ibm_cloud

# ===== IBM Cloud Object Storage =====
# Get from: IBM Cloud Console → COS instance → Service credentials
IBM_CLOUD_API_KEY=your_ibm_cloud_api_key_here
COS_API_KEY=your_cos_api_key_here
COS_INSTANCE_ID=crn:v1:bluemix:public:cloud-object-storage:global:a/<account_id>:<instance_id>::
COS_ENDPOINT=https://s3.us-east.cloud-object-storage.appdomain.cloud
COS_BUCKET_EXPERIMENTS=aios-quantum-experiments
COS_BUCKET_RESULTS=aios-quantum-results
COS_BUCKET_NAME=aios-quantum-experiments

# ===== IBM Cloudant NoSQL Database =====
# Get from: IBM Cloud Console → Cloudant instance → Service credentials
CLOUDANT_API_KEY=your_cloudant_api_key_here
CLOUDANT_HOST=<instance_id>-bluemix.cloudantnosqldb.appdomain.cloud
CLOUDANT_URL=https://<instance_id>-bluemix.cloudantnosqldb.appdomain.cloud
CLOUDANT_USERNAME=apikey-v2-<your_username>
CLOUDANT_PASSWORD=your_cloudant_password_here
CLOUDANT_DATABASE=quantum_topology
```

---

## Python Packages

### Required Packages
```bash
pip install ibm-cos-sdk       # Cloud Object Storage
pip install ibmcloudant       # Cloudant NoSQL (new SDK)
pip install ibm-watson        # Watson AI services
pip install python-dotenv     # .env file support
pip install qiskit-ibm-runtime  # Quantum computing
```

### Installed Versions (Dec 13, 2025)
| Package | Version |
|---------|---------|
| ibm-cos-sdk | 2.15.0 |
| ibmcloudant | 0.10.x |
| ibm-watson | 11.1.0 |
| ibm_cloud_sdk_core | 3.24.2 |
| python-dotenv | 1.2.1 |

---

## Testing

### Quick Connection Test
```powershell
cd c:\dev\aios-quantum
python examples/test_cloud_upload.py
```

### Expected Output
```
✓ PASS     Cloud Object Storage
✓ PASS     Cloudant Database
✓ PASS     Uploader Module
🚀 All systems operational!
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    AIOS QUANTUM CLOUD STACK                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐   │
│  │  IBM Quantum  │    │  Cloud Object │    │   Cloudant    │   │
│  │   Platform    │    │    Storage    │    │   NoSQL DB    │   │
│  │   (us-east)   │    │   (global)    │    │  (us-south)   │   │
│  └───────┬───────┘    └───────┬───────┘    └───────┬───────┘   │
│          │                    │                    │            │
│          │                    │                    │            │
│  ┌───────▼────────────────────▼────────────────────▼───────┐   │
│  │              QuantumTopologyUploader                     │   │
│  │            (src/aios_quantum/cloud/uploader.py)          │   │
│  └─────────────────────────┬───────────────────────────────┘   │
│                            │                                    │
│  ┌─────────────────────────▼───────────────────────────────┐   │
│  │              Local Development Environment               │   │
│  │                  c:\dev\aios-quantum                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Free Tier Limits

| Service | Free Limit | Current Usage |
|---------|------------|---------------|
| **COS** | 25 GB storage, 2000 requests/month | ~25 KB (0.0001%) |
| **Cloudant** | 1 GB storage, 20 reads/sec | ~0 KB (empty) |
| **Quantum** | Open plan - 10 min/month | Variable |

---

## Console Links

- **IBM Cloud Dashboard:** https://cloud.ibm.com
- **Cloud Object Storage:** https://cloud.ibm.com/objectstorage
- **Cloudant Dashboard:** https://cloud.ibm.com/services/cloudantnosqldb
- **IBM Quantum Platform:** https://quantum.ibm.com

---

## Support

- **IBM Cloud Docs:** https://cloud.ibm.com/docs
- **IBM Quantum Docs:** https://docs.quantum.ibm.com
- **Qiskit Documentation:** https://qiskit.org/documentation

---

## Security Checklist

- [ ] **Rotate all exposed keys** in IBM Cloud Console
- [ ] **Never commit** `.env` files to git
- [ ] **Use `.env.example`** as template (no real values)
- [ ] **Enable** git pre-commit hooks for secret scanning
- [ ] **Review** git history for any other exposures

See [SECRETS_PROTECTION.md](./SECRETS_PROTECTION.md) for complete security protocol.
