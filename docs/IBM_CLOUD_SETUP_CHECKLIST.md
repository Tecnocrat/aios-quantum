# IBM Cloud Setup Checklist

Quick reference for cloud storage activation. See [IBM_CLOUD_SETUP_GUIDE.md](IBM_CLOUD_SETUP_GUIDE.md) for detailed instructions.

---

## ☐ Phase 1: IBM Cloud Console (Browser)

### ☐ 1.1 Verify Account Access
- [ ] Login to https://cloud.ibm.com
- [ ] Confirm account: Tecnocrat (0eb4566b0a4640a3a59769e5d10a25d3)
- [ ] Verify region: us-east (for Quantum) or us-south (for general)

### ☐ 1.2 Provision Cloud Object Storage
- [ ] Navigate to: **Catalog** → Search "Object Storage"
- [ ] Select: **Cloud Object Storage**
- [ ] Configure:
  - Service name: `aios-quantum-storage`
  - Plan: **Lite** (25 GB free)
  - Resource group: Default
- [ ] Click: **Create**
- [ ] Save instance CRN (looks like: `crn:v1:bluemix:public:cloud-object-storage:global:a/...`)

### ☐ 1.3 Create Storage Buckets
- [ ] From COS dashboard → **Buckets** → **Create bucket**
- [ ] Bucket 1:
  - Name: `aios-quantum-topology`
  - Resiliency: Regional
  - Location: us-south (or match Quantum service region)
  - Storage class: Standard
- [ ] Click: **Create bucket**

### ☐ 1.4 Generate COS Credentials
- [ ] COS instance → **Service credentials** → **New credential**
- [ ] Configure:
  - Name: `aios-quantum-uploader`
  - Role: **Writer**
  - ✓ Include HMAC Credential
- [ ] Click: **Add**
- [ ] **Copy JSON to clipboard** (entire credential object)
- [ ] Save to password manager: **COS API Key** and **Instance ID**

### ☐ 1.5 Provision Cloudant Database
- [ ] Navigate to: **Catalog** → Search "Cloudant"
- [ ] Select: **Cloudant**
- [ ] Configure:
  - Service name: `aios-quantum-metadata`
  - Plan: **Lite** (1 GB free)
  - Region: us-south
  - Authentication: IAM and legacy
- [ ] Click: **Create**
- [ ] **Launch Dashboard** (opens new tab)

### ☐ 1.6 Create Cloudant Database
- [ ] In Cloudant dashboard: **Create Database**
- [ ] Configure:
  - Name: `quantum_topology`
  - Partitioned: No
- [ ] Click: **Create**

### ☐ 1.7 Create Cloudant Indices
- [ ] Click database name → **Design Documents** → **New Doc** → **Index**
- [ ] Index 1 (timestamp):
  ```json
  {
    "index": {"fields": ["timestamp", "backend.name"]},
    "name": "timestamp-backend-index",
    "type": "json"
  }
  ```
- [ ] Click: **Create Index**
- [ ] Index 2 (error rate):
  ```json
  {
    "index": {"fields": ["topology.statistics.mean_error"]},
    "name": "error-index",
    "type": "json"
  }
  ```
- [ ] Click: **Create Index**

### ☐ 1.8 Generate Cloudant Credentials
- [ ] Back to IBM Cloud console (close Cloudant dashboard tab)
- [ ] Cloudant service → **Service credentials** → **New credential**
- [ ] Configure:
  - Name: `aios-quantum-query-access`
  - Role: **Manager**
- [ ] Click: **Add**
- [ ] **Copy JSON to clipboard**
- [ ] Save to password manager: **Cloudant API Key**, **URL**, **Account Name**

---

## ☐ Phase 2: Local Environment (Terminal)

### ☐ 2.1 Update .env File
- [ ] Open: `c:\dev\aios-quantum\.env` in editor
- [ ] Add these lines (replace with your actual values):
  ```bash
  # IBM Cloud Object Storage
  IBM_CLOUD_API_KEY=<paste-cos-apikey-here>
  COS_INSTANCE_ID=<paste-resource_instance_id-here>
  COS_ENDPOINT=https://s3.us-south.cloud-object-storage.appdomain.cloud
  COS_BUCKET_NAME=aios-quantum-topology
  
  # IBM Cloudant Database
  CLOUDANT_API_KEY=<paste-cloudant-apikey-here>
  CLOUDANT_ACCOUNT=<paste-username-uuid-here>
  CLOUDANT_URL=<paste-url-here>
  CLOUDANT_DATABASE=quantum_topology
  ```
- [ ] Save file
- [ ] Verify `.env` is in `.gitignore` (should already be there)

### ☐ 2.2 Install Python Dependencies
- [ ] Open PowerShell in project directory
- [ ] Run:
  ```powershell
  pip install ibm-cos-sdk cloudant ibm-watson
  ```
- [ ] Wait for installation to complete (should take 1-2 minutes)
- [ ] Verify:
  ```powershell
  python -c "import ibm_boto3; print('✓ COS SDK ready')"
  python -c "from cloudant.client import Cloudant; print('✓ Cloudant ready')"
  ```

### ☐ 2.3 Test Cloud Connection
- [ ] Run test script:
  ```powershell
  python examples/test_cloud_upload.py
  ```
- [ ] Expected output should include:
  - `✓ Connected to COS`
  - `✓ Target bucket exists: aios-quantum-topology`
  - `✓ Connected to Cloudant`
  - `✓ Target database exists: quantum_topology`
  - `🚀 All systems operational!`
- [ ] If any tests fail, check [IBM_CLOUD_SETUP_GUIDE.md](IBM_CLOUD_SETUP_GUIDE.md) → Troubleshooting

---

## ☐ Phase 3: Upload Existing Data

### ☐ 3.1 Backfill Heartbeat Data
- [ ] Run backfill script:
  ```powershell
  python examples/backfill_cloud_data.py
  ```
- [ ] Expected output:
  - `Found 4 heartbeat file(s) to upload`
  - Progress indicators for each file
  - `✓ COS: cos://aios-quantum-topology/raw/cardiogram/...`
  - `✓ Cloudant: heartbeat_...`
  - `🎉 Data successfully uploaded to IBM Cloud!`

### ☐ 3.2 Verify Upload in Console
**COS Verification:**
- [ ] Open: https://cloud.ibm.com/objectstorage
- [ ] Navigate: `aios-quantum-storage` → `aios-quantum-topology` bucket
- [ ] Browse: `raw/cardiogram/2025-12-12/`
- [ ] Verify: Should see 3-4 JSON files

**Cloudant Verification:**
- [ ] Open: https://cloud.ibm.com/cloudant
- [ ] Click: `aios-quantum-metadata` → Launch Dashboard
- [ ] Select: `quantum_topology` database
- [ ] Click: **All Documents**
- [ ] Verify: Should see 4 documents with IDs like `heartbeat_2025-12-12_...`

### ☐ 3.3 Test Query
- [ ] In Cloudant dashboard → **Query** tab
- [ ] Run query:
  ```json
  {
    "selector": {
      "backend.name": "ibm_fez"
    },
    "fields": ["timestamp", "backend.name", "topology.statistics.mean_error"],
    "sort": [{"timestamp": "asc"}]
  }
  ```
- [ ] Click: **Run Query**
- [ ] Verify: Should return 3 documents (ibm_fez heartbeats)

---

## ☐ Phase 4: Validation

### ☐ 4.1 Final Checks
- [ ] All 4 heartbeats visible in COS bucket
- [ ] All 4 documents queryable in Cloudant
- [ ] No error messages in upload logs
- [ ] Storage usage shows ~26 KB in COS
- [ ] Cloudant shows ~500 bytes per document

### ☐ 4.2 Cost Monitoring
- [ ] Navigate: IBM Cloud dashboard → **Billing** → **Usage**
- [ ] Verify:
  - COS usage: < 1% of 25 GB free tier
  - Cloudant usage: < 1% of 1 GB free tier
  - Total charges: $0.00

---

## ✅ Success Criteria

You've successfully set up IBM Cloud topology storage when ALL of these are true:

- ✅ COS bucket contains 4 heartbeat JSON files
- ✅ Cloudant database has 4 documents with topology metadata
- ✅ Python can query Cloudant and retrieve heartbeats
- ✅ Test script shows "All systems operational"
- ✅ No errors in upload logs
- ✅ Storage costs remain $0/month (within free tier)

---

## 🆘 Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| 403 Forbidden (COS) | Regenerate credential with **Writer** role |
| Unauthorized (Cloudant) | Check API key is from Cloudant service, not COS |
| Bucket not found | Create bucket in COS console first |
| Database not found | Create database in Cloudant dashboard |
| Import error | Run `pip install ibm-cos-sdk cloudant` |
| Connection timeout | Increase timeout in uploader.py or check network |

**Full troubleshooting:** [IBM_CLOUD_SETUP_GUIDE.md](IBM_CLOUD_SETUP_GUIDE.md) → Troubleshooting section

---

## 📞 Support

- **Setup issues:** Check [IBM_CLOUD_SETUP_GUIDE.md](IBM_CLOUD_SETUP_GUIDE.md)
- **IBM Cloud docs:** https://cloud.ibm.com/docs
- **IBM Quantum:** https://quantum-computing.ibm.com
- **GitHub issues:** https://github.com/Tecnocrat/aios-quantum/issues

---

## 🚀 After Setup Complete

**Next steps (to be done by agent after you complete setup):**

1. Agent will integrate uploader with heartbeat workflow
2. New heartbeats will automatically upload to cloud
3. Agent will create live dashboard with cloud data
4. Together: Collect 20+ heartbeats for statistical analysis
5. Together: Explore Watson AI for pattern detection

**You're ready when:** Test script shows "All systems operational" ✅

---

**Estimated total time:** 45 minutes (15 min Console + 10 min Config + 10 min Install + 10 min Upload)

**Print this checklist** or keep it open in a browser tab while working through the setup!
