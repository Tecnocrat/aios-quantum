# IBM Cloud Topology Storage Architecture
## Parallel Infrastructure for Hypersphere Data Persistence

**Status:** Design Phase  
**Integration Target:** IBM Quantum Platform + IBM Cloud Services  
**Purpose:** Store, query, and analyze quantum error topology data at scale

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    IBM Quantum Platform                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   ibm_fez    │  │ ibm_torino   │  │  ibm_kyiv    │  ...    │
│  │  156 qubits  │  │  133 qubits  │  │  127 qubits  │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                  │
│         └──────────────────┴──────────────────┘                 │
│                            │                                     │
└────────────────────────────┼─────────────────────────────────────┘
                             │
                             │ Qiskit Runtime / IAM Auth
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│              AIOS-Quantum Local Processing Layer                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  cardiogram_processor.py                                  │   │
│  │  • Fetch job results via Qiskit Runtime                  │   │
│  │  • Calculate error topology (heights, colors, roughness) │   │
│  │  • Generate hypersphere surface vertices                 │   │
│  └────────────────┬─────────────────────────────────────────┘   │
│                   │                                              │
│  ┌────────────────▼─────────────────────────────────────────┐   │
│  │  cloud_uploader.py (NEW)                                  │   │
│  │  • IBM Cloud IAM authentication                          │   │
│  │  • Multi-service parallel upload                         │   │
│  │  • Retry logic + error handling                          │   │
│  └────────────────┬─────────────────────────────────────────┘   │
└────────────────────┼──────────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┬─────────────────┬──────────────┐
        │                         │                  │              │
┌───────▼────────┐  ┌────────────▼─────────┐  ┌────▼──────────┐  │
│ IBM Cloud      │  │ IBM Cloudant         │  │ IBM Watson    │  │
│ Object Storage │  │ NoSQL Database       │  │ AI Services   │  │
│ (COS)          │  │                      │  │               │  │
│                │  │ • Topology metadata  │  │ • Pattern     │  │
│ • Raw JSON     │  │ • Queryable indices  │  │   detection   │  │
│ • QASM files   │  │ • Time-series data   │  │ • Anomaly     │  │
│ • Surface data │  │ • Backend tracking   │  │   analysis    │  │
│ • Archival     │  │                      │  │ • Predictions │  │
└───────┬────────┘  └────────────┬─────────┘  └────┬──────────┘  │
        │                        │                  │              │
        └────────────────────────┴──────────────────┴──────────────┘
                                 │
                                 │ REST APIs / GraphQL
                                 │
┌────────────────────────────────▼─────────────────────────────────┐
│           Visualization & Analytics Frontend                     │
│  ┌─────────────────────┐  ┌─────────────────────────────────┐  │
│  │  Next.js Web App    │  │  Jupyter Notebooks              │  │
│  │  localhost:3000     │  │  • Data exploration             │  │
│  │  /hypersphere       │  │  • Statistical analysis         │  │
│  │  /topology-explorer │  │  • Machine learning models      │  │
│  └─────────────────────┘  └─────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Storage Layer Details

### 1. IBM Cloud Object Storage (COS)

**Purpose:** Durable, scalable archival of raw quantum measurement data

#### Bucket Structure
```
aios-quantum-topology/
├── raw/
│   ├── cardiogram/
│   │   ├── 2025/
│   │   │   ├── 12/
│   │   │   │   ├── cardiogram_real_2025-12-12_204822.json
│   │   │   │   ├── cardiogram_real_2025-12-12_205642.json
│   │   │   │   └── ...
│   │   └── ...
│   ├── qasm/
│   │   ├── circuits/
│   │   │   ├── cardiogram_v1_156q.qasm
│   │   │   └── ...
│   └── surfaces/
│       ├── hypersphere_surface_2025-12-12_205830.json
│       └── ...
├── processed/
│   ├── aggregated/
│   │   ├── weekly_topology_2025-W50.json
│   │   └── ...
│   └── visualizations/
│       ├── hypersphere_renders/
│       └── ...
└── backups/
    └── incremental/
```

#### Configuration
```python
# cloud_storage.py
import ibm_boto3
from ibm_botocore.client import Config

cos_client = ibm_boto3.client(
    's3',
    ibm_api_key_id=os.getenv('IBM_CLOUD_API_KEY'),
    ibm_service_instance_id=os.getenv('COS_INSTANCE_ID'),
    config=Config(signature_version='oauth'),
    endpoint_url='https://s3.us-south.cloud-object-storage.appdomain.cloud'
)

def upload_heartbeat(file_path: str, metadata: dict):
    """Upload heartbeat JSON with custom metadata"""
    object_key = f"raw/cardiogram/{metadata['timestamp'][:10]}/{file_path.name}"
    
    cos_client.upload_file(
        Filename=file_path,
        Bucket='aios-quantum-topology',
        Key=object_key,
        ExtraArgs={
            'Metadata': {
                'backend': metadata['backend'],
                'job-id': metadata['job_id'],
                'mean-error': str(metadata['mean_error']),
                'circuit-hash': metadata['circuit_hash']
            }
        }
    )
    
    return f"cos://{object_key}"
```

#### Storage Class Strategy
- **Standard:** Recent data (last 30 days) - frequent access
- **Vault:** Historical data (30-365 days) - occasional retrieval
- **Cold Vault:** Archive (>1 year) - compliance/research only

---

### 2. IBM Cloudant Database

**Purpose:** Fast querying, indexing, and time-series analysis of topology metadata

#### Database Schema

**Database:** `quantum_topology`

**Document Structure:**
```json
{
  "_id": "heartbeat_2025-12-12_204822_ibm_fez",
  "_rev": "1-abc123...",
  "type": "heartbeat",
  "timestamp": "2025-12-12T19:48:22.163283Z",
  "backend": {
    "name": "ibm_fez",
    "qubits": 156,
    "quantum_volume": 64,
    "processor_type": "falcon_r5.11l"
  },
  "job": {
    "id": "d4u7ju7g0u6s73d9f58g",
    "shots": 1024,
    "execution_time_seconds": 2.4
  },
  "circuit": {
    "hash": "sha256:a3f5c2e1...",
    "qubits_used": [96, 102, 103, 104],
    "gate_count": 452,
    "depth": 89,
    "cx_count": 0,
    "cz_count": 134
  },
  "measurements": {
    "counts": {
      "00000": 983,
      "00010": 17,
      "01000": 22,
      "00001": 1,
      "00100": 1
    },
    "total_shots": 1024,
    "unique_outcomes": 5
  },
  "topology": {
    "vertices": [
      {
        "qubit": 102,
        "position": [0.45, 0.0, 0.779],
        "height": -0.9805,
        "error": 0.0010,
        "color": [0, 119, 255]
      },
      // ... 4 more vertices
    ],
    "statistics": {
      "mean_error": 0.0080,
      "max_error": 0.0215,
      "min_error": 0.0,
      "error_variance": 8.37e-05,
      "roughness": 8.37e-05
    }
  },
  "storage": {
    "cos_url": "cos://raw/cardiogram/2025-12-12/cardiogram_real_2025-12-12_204822.json",
    "file_size_bytes": 1847,
    "checksum_sha256": "b7e4c9a2..."
  },
  "tags": ["production", "ibm_fez", "low_error"],
  "created_at": "2025-12-12T19:48:25.123Z",
  "updated_at": "2025-12-12T19:48:25.123Z"
}
```

#### Cloudant Indices
```javascript
// Index by timestamp for time-series queries
{
  "index": {
    "fields": ["timestamp", "backend.name"]
  },
  "name": "timestamp-backend-index",
  "type": "json"
}

// Index by error rate for anomaly detection
{
  "index": {
    "fields": ["topology.statistics.mean_error", "backend.name"]
  },
  "name": "error-backend-index",
  "type": "json"
}

// Geospatial index for 3D topology queries (future)
{
  "index": {
    "fields": ["topology.vertices[].position"]
  },
  "name": "spatial-topology-index",
  "type": "geospatial"
}
```

#### Query Examples
```python
# Find all high-error heartbeats
selector = {
    "topology.statistics.mean_error": {"$gt": 0.03},
    "backend.name": {"$in": ["ibm_fez", "ibm_torino"]}
}
result = cloudant_db.get_query_result(selector)

# Time-series analysis: Last 24 hours
from datetime import datetime, timedelta
now = datetime.utcnow()
yesterday = now - timedelta(days=1)

selector = {
    "timestamp": {
        "$gte": yesterday.isoformat(),
        "$lte": now.isoformat()
    }
}
result = cloudant_db.get_query_result(selector, sort=[{"timestamp": "asc"}])
```

---

### 3. IBM Watson AI Services

**Purpose:** Intelligent analysis of quantum error patterns

#### Watson Studio Integration

**Notebook:** `topology_pattern_analysis.ipynb`

```python
from ibm_watson_machine_learning import APIClient

# Connect to Watson ML
wml_credentials = {
    "url": "https://us-south.ml.cloud.ibm.com",
    "apikey": os.getenv('IBM_CLOUD_API_KEY')
}
client = APIClient(wml_credentials)

# Load topology data from Cloudant
import cloudant
db = cloudant.Cloudant(...)
heartbeats = list(db['quantum_topology'].all_docs(include_docs=True))

# Feature extraction
features = pd.DataFrame([
    {
        'backend': doc['backend']['name'],
        'mean_error': doc['topology']['statistics']['mean_error'],
        'roughness': doc['topology']['statistics']['roughness'],
        'unique_outcomes': doc['measurements']['unique_outcomes'],
        'timestamp': doc['timestamp']
    }
    for doc in heartbeats
])

# Anomaly detection with Watson AutoAI
from ibm_watson_machine_learning.experiment import AutoAI

experiment = AutoAI(wml_credentials, space_id='...')
pipeline = experiment.runs.get_run_details()

# Predict error spikes
predictions = pipeline.predict(features)
```

#### Watson Discovery (Future)
- **Corpus:** QASM circuit descriptions + topology metadata
- **Query:** "Show me all circuits with high entanglement and low error on ibm_fez"
- **Insight:** Automatically discover optimal circuit patterns

---

## 🔌 Integration Code

### cloud_uploader.py (NEW)

```python
"""
AIOS-Quantum Cloud Uploader
Parallel upload to IBM Cloud services after each heartbeat measurement
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import asyncio

import ibm_boto3
from ibm_botocore.client import Config
from cloudant.client import Cloudant
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


class QuantumTopologyUploader:
    """Manages parallel uploads to IBM Cloud storage services"""
    
    def __init__(self):
        self.cos_client = self._init_cos()
        self.cloudant_client = self._init_cloudant()
        self.watson_nlu = self._init_watson()
        
    def _init_cos(self):
        """Initialize Cloud Object Storage client"""
        return ibm_boto3.client(
            's3',
            ibm_api_key_id=os.getenv('IBM_CLOUD_API_KEY'),
            ibm_service_instance_id=os.getenv('COS_INSTANCE_ID'),
            config=Config(signature_version='oauth'),
            endpoint_url='https://s3.us-south.cloud-object-storage.appdomain.cloud'
        )
    
    def _init_cloudant(self):
        """Initialize Cloudant NoSQL database"""
        authenticator = IAMAuthenticator(os.getenv('IBM_CLOUD_API_KEY'))
        return Cloudant.iam(
            account_name=os.getenv('CLOUDANT_ACCOUNT'),
            api_key=os.getenv('IBM_CLOUD_API_KEY'),
            url=f"https://{os.getenv('CLOUDANT_ACCOUNT')}.cloudantnosqldb.appdomain.cloud",
            connect=True
        )
    
    def _init_watson(self):
        """Initialize Watson Natural Language Understanding"""
        authenticator = IAMAuthenticator(os.getenv('IBM_CLOUD_API_KEY'))
        nlu = NaturalLanguageUnderstandingV1(
            version='2022-04-07',
            authenticator=authenticator
        )
        nlu.set_service_url('https://api.us-south.natural-language-understanding.watson.cloud.ibm.com')
        return nlu
    
    async def upload_heartbeat(self, cardiogram_path: Path) -> Dict[str, str]:
        """
        Upload heartbeat data to all IBM Cloud services in parallel
        
        Returns:
            Dictionary with URLs/IDs for each uploaded resource
        """
        # Load heartbeat data
        with open(cardiogram_path, 'r') as f:
            heartbeat_data = json.load(f)
        
        # Calculate metadata
        circuit_hash = self._hash_circuit(heartbeat_data)
        timestamp = heartbeat_data['timestamp']
        backend = heartbeat_data['backend']
        
        # Parallel upload tasks
        tasks = [
            self._upload_to_cos(cardiogram_path, heartbeat_data),
            self._upload_to_cloudant(heartbeat_data, circuit_hash),
            self._analyze_with_watson(heartbeat_data)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            'cos_url': results[0] if not isinstance(results[0], Exception) else None,
            'cloudant_id': results[1] if not isinstance(results[1], Exception) else None,
            'watson_analysis': results[2] if not isinstance(results[2], Exception) else None,
            'errors': [r for r in results if isinstance(r, Exception)]
        }
    
    async def _upload_to_cos(self, file_path: Path, data: dict) -> str:
        """Upload raw JSON to Cloud Object Storage"""
        timestamp = data['timestamp']
        date_str = timestamp[:10]  # YYYY-MM-DD
        
        object_key = f"raw/cardiogram/{date_str}/{file_path.name}"
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            self.cos_client.upload_file,
            str(file_path),
            'aios-quantum-topology',
            object_key,
            {
                'Metadata': {
                    'backend': data['backend'],
                    'job-id': data.get('job_id', ''),
                    'mean-error': str(data.get('mean_qubit_error', 0)),
                    'timestamp': timestamp
                }
            }
        )
        
        return f"cos://aios-quantum-topology/{object_key}"
    
    async def _upload_to_cloudant(self, data: dict, circuit_hash: str) -> str:
        """Upload structured metadata to Cloudant database"""
        db = self.cloudant_client['quantum_topology']
        
        doc_id = f"heartbeat_{data['timestamp'].replace(':', '-').replace('.', '_')}_{data['backend']}"
        
        document = {
            '_id': doc_id,
            'type': 'heartbeat',
            'timestamp': data['timestamp'],
            'backend': {
                'name': data['backend'],
                'qubits': data.get('num_qubits', 5)
            },
            'job': {
                'id': data.get('job_id', ''),
                'shots': data.get('shots', 1024)
            },
            'circuit': {
                'hash': circuit_hash,
                'qubits_used': [96, 102, 103, 104]  # From QASM analysis
            },
            'measurements': {
                'counts': data.get('counts', {}),
                'total_shots': data.get('shots', 1024)
            },
            'topology': {
                'statistics': {
                    'mean_error': data.get('mean_qubit_error', 0),
                    'error_variance': data.get('error_variance', 0),
                    'roughness': data.get('surface_data', {}).get('roughness', 0)
                }
            },
            'created_at': datetime.utcnow().isoformat()
        }
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, db.create_document, document)
        
        return result['_id']
    
    async def _analyze_with_watson(self, data: dict) -> dict:
        """Perform AI analysis with Watson services"""
        # Create natural language description
        description = (
            f"Quantum heartbeat from {data['backend']} backend. "
            f"Mean error rate: {data.get('mean_qubit_error', 0):.4f}. "
            f"Measurement outcomes: {list(data.get('counts', {}).keys())}."
        )
        
        # Placeholder for future Watson integration
        # In production, this would call Watson NLU for sentiment/entity extraction
        # or Watson ML for anomaly detection
        
        return {
            'description': description,
            'anomaly_score': data.get('mean_qubit_error', 0) / 0.05,  # Normalized
            'recommendation': 'normal' if data.get('mean_qubit_error', 0) < 0.02 else 'investigate'
        }
    
    def _hash_circuit(self, data: dict) -> str:
        """Calculate SHA-256 hash of circuit structure"""
        # In production, hash the QASM string
        circuit_str = json.dumps(data.get('counts', {}), sort_keys=True)
        return hashlib.sha256(circuit_str.encode()).hexdigest()[:16]


# Usage example
async def main():
    uploader = QuantumTopologyUploader()
    
    cardiogram_file = Path("cardiogram_results/cardiogram_real_2025-12-12_204822.json")
    
    print(f"Uploading {cardiogram_file.name} to IBM Cloud...")
    results = await uploader.upload_heartbeat(cardiogram_file)
    
    print(f"✅ COS URL: {results['cos_url']}")
    print(f"✅ Cloudant ID: {results['cloudant_id']}")
    print(f"✅ Watson Analysis: {results['watson_analysis']}")
    
    if results['errors']:
        print(f"⚠️ Errors: {results['errors']}")


if __name__ == '__main__':
    asyncio.run(main())
```

---

## 🔐 Authentication & IAM

### Required IBM Cloud Services
1. **Cloud Object Storage** (Standard plan)
2. **Cloudant** (Lite or Standard plan)
3. **Watson Studio** (Lite plan for testing)
4. **IBM Quantum Platform** (Already configured)

### Environment Variables
```bash
# .env.cloud (DO NOT COMMIT)
IBM_CLOUD_API_KEY=<your-ibm-cloud-api-key>
COS_INSTANCE_ID=<cos-instance-crn>
COS_BUCKET_NAME=aios-quantum-topology
CLOUDANT_ACCOUNT=<cloudant-account-name>
CLOUDANT_URL=https://<account>.cloudantnosqldb.appdomain.cloud
WATSON_NLU_APIKEY=<watson-api-key>
WATSON_NLU_URL=https://api.us-south.natural-language-understanding.watson.cloud.ibm.com
```

### IAM Policies
```json
{
  "roles": [
    {
      "role_id": "crn:v1:bluemix:public:iam::::role:Writer",
      "resources": [
        {
          "service": "cloud-object-storage",
          "resource": "aios-quantum-topology"
        }
      ]
    },
    {
      "role_id": "crn:v1:bluemix:public:iam::::role:Editor",
      "resources": [
        {
          "service": "cloudantnosqldb",
          "database": "quantum_topology"
        }
      ]
    }
  ]
}
```

---

## 📊 Monitoring & Observability

### IBM Cloud Monitoring Dashboard
```
Metrics to Track:
├── Upload latency (COS, Cloudant, Watson)
├── Storage costs (GB/month)
├── API request count
├── Error rates (4xx, 5xx)
└── Heartbeat ingestion rate (beats/hour)
```

### Alerting Rules
```yaml
alerts:
  - name: High Error Rate
    condition: topology.statistics.mean_error > 0.05
    action: Send notification to Slack #quantum-alerts
  
  - name: Upload Failure
    condition: cos_upload_error OR cloudant_upload_error
    action: Retry with exponential backoff, log to file
  
  - name: Storage Quota Warning
    condition: cos_usage > 80% of quota
    action: Email admin, archive old data to Cold Vault
```

---

## 🚀 Deployment Plan

### Phase 1: Local Testing (Current)
- [x] Generate 4 heartbeats locally
- [x] Visualize in localhost:3000/hypersphere
- [ ] Set up IBM Cloud trial accounts (COS, Cloudant, Watson)

### Phase 2: Cloud Integration (Week 1)
- [ ] Implement `cloud_uploader.py`
- [ ] Test upload to COS with 10 sample heartbeats
- [ ] Create Cloudant database schema
- [ ] Verify queries work correctly

### Phase 3: Pipeline Automation (Week 2)
- [ ] Integrate uploader into `cardiogram_processor.py`
- [ ] Add automatic upload after each heartbeat measurement
- [ ] Implement retry logic and error handling
- [ ] Set up monitoring dashboard

### Phase 4: Scale Testing (Week 3-4)
- [ ] Collect 100+ heartbeats across multiple backends
- [ ] Benchmark query performance
- [ ] Optimize storage costs (compression, archival)
- [ ] Watson ML model training for anomaly detection

### Phase 5: Production (Month 2)
- [ ] Continuous heartbeat collection (1/hour)
- [ ] Real-time dashboard updates
- [ ] Automated weekly topology reports
- [ ] Research publication on quantum error landscapes

---

## 💡 Learning Resources

### IBM Cloud Documentation
- [Cloud Object Storage Getting Started](https://cloud.ibm.com/docs/cloud-object-storage)
- [Cloudant NoSQL Database](https://cloud.ibm.com/docs/Cloudant)
- [Watson Studio Tutorials](https://www.ibm.com/cloud/watson-studio)

### Quantum + Cloud Integration
- [Qiskit Runtime on IBM Cloud](https://qiskit.org/documentation/partners/qiskit_ibm_runtime/)
- [Quantum-Classical Hybrid Architectures](https://arxiv.org/abs/2101.02109)

### Code Examples
- `examples/cloud_storage_test.py` (to be created)
- `examples/cloudant_query_demo.py` (to be created)

---

## 🤝 Collaboration Notes

**User Intent:** "We both need to learn how this IBM Cloud/Quantum/AI works"

**Learning Path:**
1. **Start simple:** Upload 1 heartbeat manually to COS via IBM Cloud console
2. **Automate:** Run `cloud_uploader.py` script locally
3. **Query:** Practice Cloudant queries to filter heartbeats by error rate
4. **Visualize:** Connect Next.js app to Cloudant (live data instead of local JSON)
5. **Analyze:** Use Watson Studio notebook to find patterns
6. **Optimize:** Reduce costs, improve performance

**Pair Programming Opportunities:**
- Debugging IAM authentication errors together
- Designing optimal Cloudant indices
- Creating Watson ML anomaly detection model
- Building real-time dashboard with WebSocket updates

---

## 📈 Cost Estimation

### Lite Tier (Free)
```
Cloud Object Storage:  25 GB storage, 2,000 requests/month
Cloudant:              1 GB storage, 20 queries/second
Watson Studio:         50 capacity unit-hours/month
Total:                 $0/month (within free tier limits)
```

### Production Scale (1000 heartbeats/month)
```
COS:                   3.68 MB × 12 months = ~44 MB storage     → $0
Cloudant:              ~500 MB total                            → $0 (within 1 GB)
Watson ML:             20 hours training/month                   → $0 (within free)
Data Transfer:         Negligible (<1 GB/month)                  → $0
Total:                 $0/month (stays within free tier)
```

### Enterprise Scale (10,000 heartbeats/month)
```
COS:                   ~440 MB storage                           → $0.01/month
Cloudant:              ~5 GB storage                             → $0.25/month (Standard plan)
Watson ML:             100 hours training/month                   → $5/month
Total:                 ~$5.26/month
```

**Conclusion:** Start with free tier, scale as needed. Cost remains minimal even at research scale.

---

## ✅ Next Actions

1. **User:** Create IBM Cloud account (if not already done)
2. **User:** Provision COS bucket named `aios-quantum-topology`
3. **User:** Create Cloudant database named `quantum_topology`
4. **Agent:** Implement `cloud_uploader.py` (next file to create)
5. **Agent:** Add upload step to cardiogram processor
6. **Together:** Test first cloud upload with existing heartbeat data
7. **Together:** Query Cloudant to retrieve topology statistics
8. **Together:** Build live dashboard connected to cloud storage

---

**Ready to proceed with IBM Cloud setup?** Let me know when you have the API keys, and I'll help configure the uploader script! 🚀
