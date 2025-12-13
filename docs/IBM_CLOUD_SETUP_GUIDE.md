# IBM Cloud Setup Guide
## Step-by-Step Implementation for Topology Storage

**Status:** 🚀 READY TO IMPLEMENT  
**Target User:** Tecnocrat (jesussard@gmail.com)  
**Prerequisites:** IBM Cloud account, IBM Quantum Platform access  
**Estimated Time:** 45 minutes

---

## 📋 Pre-Flight Checklist

- [x] IBM Quantum Platform access (existing: `open-instance`)
- [x] 4 heartbeats collected locally
- [x] Hypersphere visualization working
- [x] IBM Cloud trial account active
- [x] IBM Cloud CLI installed
- [ ] API keys generated
- [ ] Cloud services provisioned

---

## Part 1: IBM Cloud Console Setup (15 min)

### Step 1.1: Verify Account Access

**Action:** Open [IBM Cloud Console](https://cloud.ibm.com)

**What You'll See:**
```
┌─────────────────────────────────────────────────────┐
│ IBM Cloud Dashboard                                  │
├─────────────────────────────────────────────────────┤
│ Account: Tecnocrat (0eb4566b0a4640a3a59769e5d10a2...) │
│ Status:  TRIAL → Upgrade to Pay-As-You-Go           │
│                                                      │
│ Resource summary:                                    │
│ • 1 service (Qiskit Runtime)                        │
│ • Region: us-east                                    │
└─────────────────────────────────────────────────────┘
```

**Verify:**
- ✓ Account status is ACTIVE
- ✓ Resource group "Default" exists
- ✓ Quantum Computing service visible

---

### Step 1.2: Create Cloud Object Storage Service

**Navigation:** 
1. Click **Catalog** (top navigation)
2. Search: `Object Storage`
3. Click **Cloud Object Storage**

**Configuration:**
```yaml
Service Name: aios-quantum-storage
Plan:         Lite (Free - 25 GB storage)
              └─ OR: Standard (Pay-as-you-go)
Resource Group: Default
Location:     Global (automatically selected)
Tags:         quantum, topology, aios
```

**Click:** `Create` button (bottom right)

**Expected Result:**
```
✓ Service created successfully
  Instance ID: crn:v1:bluemix:public:cloud-object-storage:global:a/...
  Dashboard: Available
```

**Screenshot Reference:** See attachment showing COS provisioning page

---

### Step 1.3: Create Storage Buckets

**Navigation:** 
1. From COS dashboard, click **Buckets** (left sidebar)
2. Click **Create bucket** button

**Bucket 1: Raw Data**
```yaml
Bucket name: aios-quantum-topology
Resiliency:  Regional
Location:    us-south (or us-east - match Quantum service)
Storage class: Standard
```

**Bucket 2: Processed Data (Optional for now)**
```yaml
Bucket name: aios-quantum-analytics
Resiliency:  Regional  
Location:    us-south
Storage class: Vault (cheaper for infrequent access)
```

**Click:** `Create bucket` for each

**Expected Structure:**
```
aios-quantum-storage (Instance)
├── aios-quantum-topology/
│   ├── raw/
│   │   └── cardiogram/
│   └── surfaces/
└── aios-quantum-analytics/
    └── aggregated/
```

---

### Step 1.4: Generate Service Credentials

**Navigation:**
1. From COS instance page, click **Service credentials** (left sidebar)
2. Click **New credential** button

**Configuration:**
```yaml
Name:  aios-quantum-uploader
Role:  Writer (allows upload/read)
       └─ NOT Manager (we don't need bucket creation here)
       
Service ID: Auto-generate (default)

Advanced Options:
  ✓ Include HMAC Credential (for S3 compatibility)
```

**Click:** `Add` button

**Expected Output:** JSON credentials displayed
```json
{
  "apikey": "YOUR_API_KEY_HERE_KEEP_SECRET",
  "cos_hmac_keys": {
    "access_key_id": "...",
    "secret_access_key": "..."
  },
  "endpoints": "https://control.cloud-object-storage.cloud.ibm.com/v2/endpoints",
  "iam_apikey_description": "Auto-generated for key ...",
  "iam_serviceid_crn": "crn:v1:bluemix:public:iam-identity::...",
  "resource_instance_id": "crn:v1:bluemix:public:cloud-object-storage:global:..."
}
```

**CRITICAL:** Click **Copy** icon → Save to password manager NOW

---

### Step 1.5: Create Cloudant Database Service

**Navigation:**
1. Back to main dashboard → **Catalog**
2. Search: `Cloudant`
3. Click **Cloudant**

**Configuration:**
```yaml
Service Name: aios-quantum-metadata
Plan:         Lite (Free - 1 GB storage, 20 queries/sec)
              └─ OR: Standard ($0.25/GB over 1 GB)
Region:       us-south
Authentication: IAM and legacy credentials
```

**Click:** `Create`

**Expected Result:**
```
✓ Cloudant instance provisioned
  URL: https://YOUR-UUID.cloudantnosqldb.appdomain.cloud
  Dashboard: Available
```

---

### Step 1.6: Create Cloudant Database

**Navigation:**
1. From Cloudant dashboard, click **Launch Dashboard** (opens in new tab)
2. Click **Create Database** button

**Configuration:**
```yaml
Database name: quantum_topology
Partitioned:   No (standard database)
```

**Click:** `Create`

**Then Create Indices:**

Click database name → **Design Documents** tab → **New Doc** → Choose **Index**

**Index 1: Timestamp + Backend**
```json
{
  "index": {
    "fields": ["timestamp", "backend.name"]
  },
  "name": "timestamp-backend-index",
  "type": "json"
}
```

**Index 2: Error Rate**
```json
{
  "index": {
    "fields": ["topology.statistics.mean_error"]
  },
  "name": "error-index",
  "type": "json"
}
```

**Click:** `Create Index` for each

---

### Step 1.7: Generate Cloudant Credentials

**Navigation:**
1. Back to IBM Cloud console (close Cloudant dashboard tab)
2. From Cloudant service instance → **Service credentials**
3. Click **New credential**

**Configuration:**
```yaml
Name: aios-quantum-query-access
Role: Manager (allows read/write/admin)
```

**Click:** `Add`

**Expected Output:**
```json
{
  "apikey": "ANOTHER_API_KEY_KEEP_SECRET",
  "host": "YOUR-UUID.cloudantnosqldb.appdomain.cloud",
  "iam_apikey_description": "Auto-generated",
  "url": "https://YOUR-UUID.cloudantnosqldb.appdomain.cloud",
  "username": "YOUR-UUID"
}
```

**CRITICAL:** Copy and save securely

---

## Part 2: Local Environment Configuration (10 min)

### Step 2.1: Update .env File

**File:** `c:\dev\aios-quantum\.env`

**Add these lines:**
```bash
# ===== IBM CLOUD OBJECT STORAGE =====
IBM_CLOUD_API_KEY=<paste-your-cos-apikey-here>
COS_INSTANCE_ID=<paste-resource_instance_id-here>
COS_ENDPOINT=https://s3.us-south.cloud-object-storage.appdomain.cloud
COS_BUCKET_NAME=aios-quantum-topology

# ===== IBM CLOUDANT DATABASE =====
CLOUDANT_API_KEY=<paste-your-cloudant-apikey-here>
CLOUDANT_ACCOUNT=<paste-username-uuid-here>
CLOUDANT_URL=<paste-url-here>
CLOUDANT_DATABASE=quantum_topology

# ===== EXISTING QUANTUM CREDENTIALS (keep these) =====
IBM_QUANTUM_TOKEN=<your-existing-token>
IBM_QUANTUM_INSTANCE=ibm-q/open/main
```

**Example (SANITIZED):**
```bash
IBM_CLOUD_API_KEY=xAbC123_dEf456-gHi789KlMnOpQrStUvWxYz
COS_INSTANCE_ID=crn:v1:bluemix:public:cloud-object-storage:global:a/0eb4566b...
COS_ENDPOINT=https://s3.us-south.cloud-object-storage.appdomain.cloud
COS_BUCKET_NAME=aios-quantum-topology

CLOUDANT_API_KEY=yZaB987_fEdC654-hGiKjLmNoPqRsTuVwXyZ
CLOUDANT_ACCOUNT=a1b2c3d4-e5f6-7890-abcd-ef1234567890-bluemix
CLOUDANT_URL=https://a1b2c3d4-e5f6-7890-abcd-ef1234567890-bluemix.cloudantnosqldb.appdomain.cloud
CLOUDANT_DATABASE=quantum_topology
```

**Security Check:**
```powershell
# Verify .gitignore includes .env
Get-Content .gitignore | Select-String ".env"
# Expected output: .env
```

---

### Step 2.2: Install Required Python Packages

**Run in terminal:**
```powershell
# Activate your conda environment if using one
# conda activate aios-quantum

pip install ibm-cos-sdk
pip install cloudant
pip install ibm-watson
pip install python-dotenv
```

**Expected output:**
```
Successfully installed ibm-cos-sdk-2.13.4
Successfully installed cloudant-2.15.0
Successfully installed ibm-watson-8.0.0
Successfully installed python-dotenv-1.0.0
```

**Verify installation:**
```powershell
python -c "import ibm_boto3; print('✓ COS SDK ready')"
python -c "from cloudant.client import Cloudant; print('✓ Cloudant ready')"
```

---

## Part 3: Implementation (20 min)

### Step 3.1: Create Cloud Uploader Module

**Agent Action:** I'll create `src/aios_quantum/cloud/uploader.py` now

**File:** `src/aios_quantum/cloud/uploader.py`

This will implement:
- `QuantumTopologyUploader` class
- Parallel uploads to COS + Cloudant
- Error handling and retry logic
- Connection to existing heartbeat system

---

### Step 3.2: Test Connection

**Manual test script:** `examples/test_cloud_upload.py`

**Run:**
```powershell
python examples/test_cloud_upload.py
```

**Expected output:**
```
Connecting to IBM Cloud services...
✓ Cloud Object Storage: Connected (aios-quantum-topology)
✓ Cloudant Database: Connected (quantum_topology)

Testing upload with sample heartbeat...
✓ Uploaded to COS: cos://raw/cardiogram/2025-12-12/test_heartbeat.json
✓ Created Cloudant doc: heartbeat_test_2025-12-12_20-00-00

All systems operational! 🚀
```

---

### Step 3.3: Upload Existing Heartbeats

**Script:** `examples/backfill_cloud_data.py`

**Run:**
```powershell
python examples/backfill_cloud_data.py
```

**What it does:**
1. Scans `cardiogram_results/` for existing JSON files
2. Uploads each to COS bucket
3. Creates corresponding Cloudant documents
4. Links hypersphere surface data

**Expected output:**
```
Found 4 heartbeat files to upload:
  1. cardiogram_real_2025-12-12_204822.json
  2. cardiogram_real_2025-12-12_205642.json
  3. cardiogram_real_2025-12-12_205736.json
  4. (from torino) real_beat_001_2025-12-12_002752.json

Uploading to IBM Cloud...
[████████████████████] 4/4 complete

✓ COS: 4 files uploaded (25.8 KB total)
✓ Cloudant: 4 documents created
✓ Surface data: 1 hypersphere linked

View in IBM Cloud Console:
https://cloud.ibm.com/objectstorage/crn%3Av1%3A...
```

---

### Step 3.4: Verify in Cloud Console

**COS Bucket Check:**
1. Open IBM Cloud → Cloud Object Storage → `aios-quantum-topology`
2. Navigate to `raw/cardiogram/2025-12-12/`
3. You should see 4 JSON files

**Cloudant Database Check:**
1. Open IBM Cloud → Cloudant → `quantum_topology`
2. Click database → **All Documents**
3. You should see 4 documents with IDs like `heartbeat_2025-12-12_204822_ibm_fez`

**Query Test:**
```json
{
  "selector": {
    "backend.name": "ibm_fez",
    "topology.statistics.mean_error": {
      "$lt": 0.01
    }
  },
  "fields": ["timestamp", "backend.name", "topology.statistics.mean_error"],
  "sort": [{"timestamp": "asc"}]
}
```

**Expected result:** 3 documents (the low-error ibm_fez heartbeats)

---

## Part 4: Integration with Heartbeat System (Automatic)

### Step 4.1: Update Cardiogram Processor

**Agent Action:** I'll modify `src/aios_quantum/circuits/consciousness_circuits.py`

**What changes:**
```python
# OLD: Save to local file only
save_cardiogram_results(data, "cardiogram_results/")

# NEW: Save locally AND upload to cloud
save_cardiogram_results(data, "cardiogram_results/")
await cloud_uploader.upload_heartbeat(data)  # Parallel upload
```

**Result:** Every new heartbeat automatically uploads to IBM Cloud

---

### Step 4.2: Enable Cloud Uploads

**File:** `src/aios_quantum/config.py`

**Add configuration:**
```python
@dataclass
class CloudConfig:
    """IBM Cloud integration settings"""
    enabled: bool = True  # Set to False to disable cloud uploads
    retry_attempts: int = 3
    retry_delay: float = 2.0  # seconds
    upload_timeout: float = 30.0  # seconds
```

**Usage in code:**
```python
if CloudConfig.enabled:
    await uploader.upload_heartbeat(heartbeat_data)
else:
    logger.info("Cloud uploads disabled, saving locally only")
```

---

## Part 5: Verification & Monitoring (Ongoing)

### Step 5.1: Query Cloudant from Python

**Example: Get latest heartbeats**
```python
from cloudant.client import Cloudant
import os
from dotenv import load_dotenv

load_dotenv()

client = Cloudant.iam(
    account_name=os.getenv('CLOUDANT_ACCOUNT'),
    api_key=os.getenv('CLOUDANT_API_KEY'),
    connect=True
)

db = client['quantum_topology']

# Get last 10 heartbeats
result = db.get_query_result(
    selector={'type': 'heartbeat'},
    sort=[{'timestamp': 'desc'}],
    limit=10
)

for doc in result:
    print(f"{doc['timestamp']}: {doc['backend']['name']} - {doc['topology']['statistics']['mean_error']:.4f}")
```

**Expected output:**
```
2025-12-12T19:57:36: ibm_fez - 0.0080
2025-12-12T19:56:42: ibm_fez - 0.0098
2025-12-12T19:48:22: ibm_fez - 0.0080
2025-12-11T23:27:52: ibm_torino - 0.0395
```

---

### Step 5.2: Build Live Dashboard (Next Phase)

**Goal:** Replace local JSON files with cloud data in Next.js app

**API Route:** `web/src/app/api/surface/cloud/route.ts`
```typescript
// Fetch from Cloudant instead of local filesystem
import { Cloudant } from '@ibm-cloud/cloudant';

export async function GET() {
  const client = Cloudant.newInstance({
    serviceUrl: process.env.CLOUDANT_URL,
    authenticator: new IamAuthenticator({
      apikey: process.env.CLOUDANT_API_KEY
    })
  });
  
  const db = client.db.use('quantum_topology');
  const result = await db.find({
    selector: { type: 'heartbeat' },
    sort: [{ timestamp: 'desc' }],
    limit: 20
  });
  
  return Response.json(result.docs);
}
```

**Update visualization:** Fetch from `/api/surface/cloud` → Real-time updates!

---

## 🎯 Success Criteria

**You've successfully set up IBM Cloud topology storage when:**

- [x] COS bucket contains 4+ heartbeat JSON files
- [x] Cloudant database has 4+ documents with topology data
- [x] Python script can query Cloudant and retrieve heartbeats
- [x] New heartbeats automatically upload to cloud
- [x] Hypersphere visualization can be fed from cloud data
- [x] No API errors in logs
- [x] Storage costs remain $0/month (within free tier)

---

## 🆘 Troubleshooting

### Issue: "403 Forbidden" when uploading to COS

**Cause:** API key doesn't have Writer role

**Fix:**
1. Go to COS service credentials
2. Delete existing credential
3. Create new credential with "Writer" role (not Reader)
4. Update `.env` with new API key

---

### Issue: "CouchDB error: unauthorized"

**Cause:** Cloudant API key or URL incorrect

**Fix:**
1. Verify `CLOUDANT_URL` matches exactly (including `https://`)
2. Check `CLOUDANT_API_KEY` is from Cloudant service, not COS
3. Test connection: `curl -u $CLOUDANT_API_KEY:$CLOUDANT_API_KEY $CLOUDANT_URL`

---

### Issue: Import error "No module named 'ibm_boto3'"

**Cause:** Packages not installed in correct Python environment

**Fix:**
```powershell
# Check which Python
python --version
which python

# Reinstall in active environment
pip install --upgrade ibm-cos-sdk cloudant
```

---

### Issue: Uploads timeout after 30 seconds

**Cause:** Large files or slow connection

**Fix:** Increase timeout in `uploader.py`:
```python
upload_timeout: float = 120.0  # 2 minutes
```

---

## 📊 Cost Monitoring

**Free Tier Limits:**
- **COS Lite:** 25 GB storage, 2,000 requests/month
- **Cloudant Lite:** 1 GB storage, 20 queries/second

**Current Usage Projection:**
- 4 heartbeats = 25.8 KB (0.1% of COS limit)
- 1000 heartbeats/year = 3.68 MB (14.7% of COS limit)
- Cloudant: ~500 KB for 1000 heartbeats (0.05% of limit)

**You won't exceed free tier unless you collect 10,000+ heartbeats**

**To monitor:** IBM Cloud dashboard → Billing → Usage

---

## 🚀 Next Steps After Setup

1. **Collect more heartbeats:** Run on ibm_kyiv, ibm_sherbrooke, ibm_quebec
2. **Time-series analysis:** Query Cloudant for error trends over time
3. **Anomaly detection:** Use Watson ML to flag unusual error spikes
4. **Live dashboard:** Connect Next.js to Cloudant for real-time updates
5. **Automated reports:** Weekly topology summaries via email/Slack

---

## 📞 Support Resources

**IBM Cloud Docs:**
- [Cloud Object Storage](https://cloud.ibm.com/docs/cloud-object-storage)
- [Cloudant](https://cloud.ibm.com/docs/Cloudant)

**AIOS Quantum Docs:**
- [IBM_CLOUD_TOPOLOGY_STORAGE.md](./IBM_CLOUD_TOPOLOGY_STORAGE.md) - Architecture
- [HYPERSPHERE_DATA_ANALYSIS.md](./HYPERSPHERE_DATA_ANALYSIS.md) - Data analysis

**Community:**
- IBM Quantum Slack: quantum-computing.ibm.com/community
- GitHub Issues: github.com/Tecnocrat/aios-quantum/issues

---

**Ready to begin?** Start with Part 1, Step 1.1 → Open IBM Cloud Console! 🎮
