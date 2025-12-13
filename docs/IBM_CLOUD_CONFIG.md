# IBM Cloud Configuration Reference
## AIOS Quantum Project

**Last Updated:** December 13, 2025  
**Status:** ✅ FULLY CONFIGURED AND TESTED

---

## Account Information

| Property | Value |
|----------|-------|
| **Account Name** | Tecnocrat |
| **Account ID** | `0eb4566b0a4640a3a59769e5d10a25d3` |
| **User** | jesussard@gmail.com |
| **Resource Group** | Default |

---

## IBM Cloud CLI

| Property | Value |
|----------|-------|
| **Version** | 2.40.0 |
| **Install Path** | `C:\Program Files\IBM\Cloud\bin\ibmcloud.exe` |
| **Install Date** | December 13, 2025 |
| **Config Path** | `C:\Users\jesus\.bluemix\` |

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
| **Instance CRN** | `crn:v1:bluemix:public:cloud-object-storage:global:a/0eb4566b0a4640a3a59769e5d10a25d3:b0bb0704-eefc-4b49-bdeb-bf14b2aaf189::` |

### Credentials
| Property | Value |
|----------|-------|
| **Credential Name** | cos-aios-key |
| **Role** | Manager |
| **API Key** | `Gp4CuMx_1Yf5T9riqivzpA84pXIdo-vzOrd9J536ZhPo` |

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
| **Instance GUID** | `d119da9c-3fcc-4622-8626-ab634b68d490` |

### Credentials
| Property | Value |
|----------|-------|
| **Credential Name** | cloudant-aios-key |
| **Role** | Manager |
| **API Key** | `4968opk2dXdmpjH-tRV0Vatsik5e-45_Kqgv3e0q-Jf4` |
| **Host** | `c8de5391-a794-410b-b35a-27c03909ea07-bluemix.cloudantnosqldb.appdomain.cloud` |

### URL
```
https://c8de5391-a794-410b-b35a-27c03909ea07-bluemix.cloudantnosqldb.appdomain.cloud
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
| **Instance CRN** | `crn:v1:bluemix:public:quantum-computing:us-east:a/0eb4566b0a4640a3a59769e5d10a25d3:1acc9085-376e-430c-98ef-3d0753ad1fe6::` |

### Available Backends
| Backend | Qubits | Status |
|---------|--------|--------|
| ibm_fez | 156 | Available |
| ibm_torino | 133 | Available |
| ibm_kyiv | 156 | Available |
| ibm_sherbrooke | 127 | Available |

### Authentication Token
```
IBM_QUANTUM_TOKEN=Th5QSXWUZ-QMgaUw8ZJuTPEtQS270jlZSs_pkkggToCp
```

---

## Environment Variables (.env)

```bash
# ===== IBM Quantum Configuration =====
IBM_QUANTUM_TOKEN=Th5QSXWUZ-QMgaUw8ZJuTPEtQS270jlZSs_pkkggToCp
IBM_QUANTUM_INSTANCE=crn:v1:bluemix:public:quantum-computing:us-east:a/0eb4566b0a4640a3a59769e5d10a25d3:1acc9085-376e-430c-98ef-3d0753ad1fe6::
IBM_QUANTUM_CHANNEL=ibm_cloud

# ===== IBM Cloud Object Storage =====
IBM_CLOUD_API_KEY=Gp4CuMx_1Yf5T9riqivzpA84pXIdo-vzOrd9J536ZhPo
COS_API_KEY=Gp4CuMx_1Yf5T9riqivzpA84pXIdo-vzOrd9J536ZhPo
COS_INSTANCE_ID=crn:v1:bluemix:public:cloud-object-storage:global:a/0eb4566b0a4640a3a59769e5d10a25d3:b0bb0704-eefc-4b49-bdeb-bf14b2aaf189::
COS_ENDPOINT=https://s3.us-east.cloud-object-storage.appdomain.cloud
COS_BUCKET_EXPERIMENTS=aios-quantum-experiments
COS_BUCKET_RESULTS=aios-quantum-results
COS_BUCKET_NAME=aios-quantum-experiments

# ===== IBM Cloudant NoSQL Database =====
CLOUDANT_API_KEY=4968opk2dXdmpjH-tRV0Vatsik5e-45_Kqgv3e0q-Jf4
CLOUDANT_HOST=c8de5391-a794-410b-b35a-27c03909ea07-bluemix.cloudantnosqldb.appdomain.cloud
CLOUDANT_URL=https://c8de5391-a794-410b-b35a-27c03909ea07-bluemix.cloudantnosqldb.appdomain.cloud
CLOUDANT_USERNAME=apikey-v2-1n5hz0r8my3gblej1ol18tf96gsgda0axrvok5t1h14i
CLOUDANT_PASSWORD=a125cd70d1dbdc6c1a5e1dcab90bedd0
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
