"""
IBM Cloud Object Storage client for AIOS Quantum.

Provides persistence for quantum experiments and results.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

from dotenv import load_dotenv

logger = logging.getLogger("aios_quantum.cloud.storage")


@dataclass
class StorageConfig:
    """Configuration for IBM Cloud Object Storage."""
    
    api_key: str
    instance_id: str
    endpoint: str
    bucket_experiments: str
    bucket_results: str
    
    @classmethod
    def from_env(cls) -> "StorageConfig":
        """Load configuration from environment variables."""
        load_dotenv()
        
        api_key = os.getenv("COS_API_KEY")
        if not api_key:
            raise ValueError("COS_API_KEY environment variable is required")
        
        return cls(
            api_key=api_key,
            instance_id=os.getenv("COS_INSTANCE_ID", ""),
            endpoint=os.getenv("COS_ENDPOINT", "https://s3.us-east.cloud-object-storage.appdomain.cloud"),
            bucket_experiments=os.getenv("COS_BUCKET_EXPERIMENTS", "aios-quantum-experiments"),
            bucket_results=os.getenv("COS_BUCKET_RESULTS", "aios-quantum-results"),
        )


class CloudStorage:
    """
    IBM Cloud Object Storage client for quantum experiment data.
    
    Features:
    - Store experiment definitions
    - Persist quantum results
    - Retrieve historical data
    - List experiments by tags
    """
    
    def __init__(self, config: Optional[StorageConfig] = None):
        """Initialize Cloud Storage client."""
        self._config = config or StorageConfig.from_env()
        self._client = None
        self._resource = None
        
    def _get_client(self):
        """Lazy-load the IBM COS client."""
        if self._client is None:
            try:
                import ibm_boto3
                from ibm_botocore.client import Config
                
                self._client = ibm_boto3.client(
                    "s3",
                    ibm_api_key_id=self._config.api_key,
                    ibm_service_instance_id=self._config.instance_id,
                    config=Config(signature_version="oauth"),
                    endpoint_url=self._config.endpoint,
                )
                logger.info(f"Connected to IBM Cloud Object Storage")
            except ImportError:
                logger.warning("ibm-cos-sdk not installed. Install with: pip install ibm-cos-sdk")
                raise
        return self._client
    
    def save_experiment(self, experiment_id: str, data: Dict[str, Any]) -> str:
        """
        Save experiment definition to cloud.
        
        Args:
            experiment_id: Unique experiment identifier
            data: Experiment configuration and metadata
            
        Returns:
            Object key (path) in the bucket
        """
        client = self._get_client()
        
        # Add timestamp
        data["saved_at"] = datetime.now().isoformat()
        
        key = f"experiments/{experiment_id}/definition.json"
        
        client.put_object(
            Bucket=self._config.bucket_experiments,
            Key=key,
            Body=json.dumps(data, indent=2, default=str),
            ContentType="application/json",
        )
        
        logger.info(f"Saved experiment {experiment_id} to cloud")
        return key
    
    def save_result(self, experiment_id: str, job_id: str, result: Dict[str, Any]) -> str:
        """
        Save quantum execution result to cloud.
        
        Args:
            experiment_id: Experiment identifier
            job_id: IBM Quantum job ID
            result: Execution results
            
        Returns:
            Object key (path) in the bucket
        """
        client = self._get_client()
        
        result["saved_at"] = datetime.now().isoformat()
        result["experiment_id"] = experiment_id
        result["job_id"] = job_id
        
        key = f"results/{experiment_id}/{job_id}.json"
        
        client.put_object(
            Bucket=self._config.bucket_results,
            Key=key,
            Body=json.dumps(result, indent=2, default=str),
            ContentType="application/json",
        )
        
        logger.info(f"Saved result for job {job_id} to cloud")
        return key
    
    def load_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """Load experiment definition from cloud."""
        client = self._get_client()
        
        key = f"experiments/{experiment_id}/definition.json"
        
        response = client.get_object(
            Bucket=self._config.bucket_experiments,
            Key=key,
        )
        
        return json.loads(response["Body"].read().decode("utf-8"))
    
    def load_result(self, experiment_id: str, job_id: str) -> Dict[str, Any]:
        """Load result from cloud."""
        client = self._get_client()
        
        key = f"results/{experiment_id}/{job_id}.json"
        
        response = client.get_object(
            Bucket=self._config.bucket_results,
            Key=key,
        )
        
        return json.loads(response["Body"].read().decode("utf-8"))
    
    def list_experiments(self, prefix: str = "") -> List[str]:
        """List all experiment IDs in cloud storage."""
        client = self._get_client()
        
        response = client.list_objects_v2(
            Bucket=self._config.bucket_experiments,
            Prefix=f"experiments/{prefix}",
            Delimiter="/",
        )
        
        experiments = []
        for prefix_obj in response.get("CommonPrefixes", []):
            # Extract experiment ID from path
            exp_id = prefix_obj["Prefix"].split("/")[1]
            experiments.append(exp_id)
        
        return experiments
    
    def list_results(self, experiment_id: str) -> List[str]:
        """List all result job IDs for an experiment."""
        client = self._get_client()
        
        response = client.list_objects_v2(
            Bucket=self._config.bucket_results,
            Prefix=f"results/{experiment_id}/",
        )
        
        job_ids = []
        for obj in response.get("Contents", []):
            # Extract job ID from filename
            filename = obj["Key"].split("/")[-1]
            if filename.endswith(".json"):
                job_ids.append(filename[:-5])
        
        return job_ids


# Convenience function
def get_storage() -> CloudStorage:
    """Get a configured CloudStorage instance."""
    return CloudStorage()
