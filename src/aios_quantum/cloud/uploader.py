"""
IBM Cloud Uploader for Quantum Topology Data

Parallel uploads to Cloud Object Storage and Cloudant Database
"""

import os
import json
import hashlib
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
from dataclasses import dataclass

import ibm_boto3
from ibm_botocore.client import Config
from ibm_botocore.exceptions import ClientError
from ibmcloudant.cloudant_v1 import CloudantV1, Document
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core import ApiException
from dotenv import load_dotenv

logger = logging.getLogger("aios_quantum.cloud.uploader")


@dataclass
class UploadResult:
    """Result of multi-service upload operation"""
    success: bool
    cos_url: Optional[str] = None
    cloudant_id: Optional[str] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class QuantumTopologyUploader:
    """
    Manages parallel uploads to IBM Cloud services
    
    Features:
    - Cloud Object Storage (COS) for raw JSON archival
    - Cloudant NoSQL database for queryable metadata
    - Async parallel uploads for performance
    - Automatic retry with exponential backoff
    - Error handling and logging
    
    Usage:
        uploader = QuantumTopologyUploader()
        result = await uploader.upload_heartbeat(Path("cardiogram.json"))
        
        if result.success:
            print(f"✓ Uploaded to {result.cos_url}")
            print(f"✓ Cloudant doc: {result.cloudant_id}")
    """
    
    def __init__(self):
        """Initialize cloud service clients"""
        load_dotenv()
        
        # Configuration
        self.cos_endpoint = os.getenv(
            'COS_ENDPOINT',
            'https://s3.us-south.cloud-object-storage.appdomain.cloud'
        )
        self.cos_bucket = os.getenv(
            'COS_BUCKET_NAME', 'aios-quantum-topology'
        )
        self.cloudant_db_name = os.getenv(
            'CLOUDANT_DATABASE', 'quantum_topology'
        )
        
        # Initialize clients
        self.cos_client = self._init_cos()
        self.cloudant_client = self._init_cloudant()
        
        logger.info("QuantumTopologyUploader initialized")
    
    def _init_cos(self):
        """Initialize IBM Cloud Object Storage client"""
        api_key = os.getenv('IBM_CLOUD_API_KEY')
        instance_id = os.getenv('COS_INSTANCE_ID')
        
        if not api_key or not instance_id:
            logger.warning("COS credentials not found - uploads will fail")
            return None
        
        try:
            client = ibm_boto3.client(
                's3',
                ibm_api_key_id=api_key,
                ibm_service_instance_id=instance_id,
                config=Config(signature_version='oauth'),
                endpoint_url=self.cos_endpoint
            )
            
            # Test connection
            client.list_buckets()
            logger.info(f"✓ Connected to COS: {self.cos_endpoint}")
            return client
            
        except Exception as e:
            logger.error(f"Failed to initialize COS client: {e}")
            return None
    
    def _init_cloudant(self):
        """Initialize IBM Cloudant NoSQL database client using ibmcloudant SDK"""
        api_key = os.getenv('CLOUDANT_API_KEY')
        url = os.getenv('CLOUDANT_URL')
        
        if not api_key or not url:
            logger.warning("Cloudant credentials not found - uploads will fail")
            return None
        
        try:
            # Create IAM authenticator
            authenticator = IAMAuthenticator(api_key)
            
            # Create Cloudant service client
            client = CloudantV1(authenticator=authenticator)
            client.set_service_url(url)
            
            # Test connection
            response = client.get_all_dbs()
            dbs = response.get_result()
            logger.info(f"✓ Connected to Cloudant: {url}")
            logger.info(f"  Available databases: {dbs}")
            return client
            
        except Exception as e:
            logger.error(f"Failed to initialize Cloudant client: {e}")
            return None
    
    async def upload_heartbeat(
        self, 
        file_path: Path,
        retry_attempts: int = 3,
        retry_delay: float = 2.0
    ) -> UploadResult:
        """
        Upload heartbeat data to all IBM Cloud services in parallel
        
        Args:
            file_path: Path to heartbeat JSON file
            retry_attempts: Number of retries on failure
            retry_delay: Delay between retries (seconds)
            
        Returns:
            UploadResult with success status and service URLs/IDs
        """
        if not file_path.exists():
            return UploadResult(
                success=False,
                errors=[f"File not found: {file_path}"]
            )
        
        # Load heartbeat data
        try:
            with open(file_path, 'r') as f:
                heartbeat_data = json.load(f)
        except json.JSONDecodeError as e:
            return UploadResult(
                success=False,
                errors=[f"Invalid JSON in {file_path}: {e}"]
            )
        
        # Calculate metadata
        circuit_hash = self._hash_file(file_path)
        
        # Parallel upload with retries
        for attempt in range(retry_attempts):
            try:
                tasks = []
                
                if self.cos_client:
                    tasks.append(
                        self._upload_to_cos_with_retry(file_path, heartbeat_data, attempt)
                    )
                
                if self.cloudant_client:
                    tasks.append(
                        self._upload_to_cloudant_with_retry(
                            heartbeat_data,
                            circuit_hash,
                            attempt
                        )
                    )
                
                if not tasks:
                    return UploadResult(
                        success=False,
                        errors=["No cloud services configured"]
                    )
                
                results = await asyncio.gather(
                    *tasks, return_exceptions=True
                )
                
                # Process results
                cos_url = None
                cloudant_id = None
                errors = []
                
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        errors.append(f"Service {i} error: {str(result)}")
                    elif isinstance(result, str):
                        # COS returns URL string
                        if result.startswith('cos://'):
                            cos_url = result
                        # Cloudant returns doc ID
                        else:
                            cloudant_id = result
                
                # Check if at least one service succeeded
                if cos_url or cloudant_id:
                    logger.info(
                        f"✓ Heartbeat uploaded (attempt {attempt + 1}): "
                        f"COS={bool(cos_url)}, Cloudant={bool(cloudant_id)}"
                    )
                    return UploadResult(
                        success=True,
                        cos_url=cos_url,
                        cloudant_id=cloudant_id,
                        errors=errors if errors else None
                    )
                
                # All failed, retry
                if attempt < retry_attempts - 1:
                    # Exponential backoff
                    await asyncio.sleep(retry_delay * (2 ** attempt))
                    
            except Exception as e:
                logger.error(f"Upload attempt {attempt + 1} failed: {e}")
                if attempt < retry_attempts - 1:
                    await asyncio.sleep(retry_delay * (2 ** attempt))
        
        return UploadResult(
            success=False,
            errors=[f"All {retry_attempts} upload attempts failed"]
        )
    
    async def _upload_to_cos_with_retry(
        self, 
        file_path: Path, 
        data: dict,
        attempt: int
    ) -> str:
        """Upload raw JSON to Cloud Object Storage"""
        timestamp = data.get('timestamp', datetime.utcnow().isoformat())
        date_str = timestamp[:10]  # YYYY-MM-DD
        
        # Object key: raw/cardiogram/YYYY-MM-DD/filename.json
        object_key = (
            f"raw/cardiogram/{date_str}/{file_path.name}"
        )
        
        loop = asyncio.get_event_loop()
        
        try:
            await loop.run_in_executor(
                None,
                lambda: self.cos_client.upload_file(
                    Filename=str(file_path),
                    Bucket=self.cos_bucket,
                    Key=object_key,
                    ExtraArgs={
                        'Metadata': {
                            'backend': data.get('backend', 'unknown'),
                            'job-id': data.get('job_id', ''),
                            'mean-error': str(
                                data.get('mean_qubit_error', 0)
                            ),
                            'timestamp': timestamp,
                            'upload-attempt': str(attempt + 1)
                        }
                    }
                )
            )
            
            url = f"cos://{self.cos_bucket}/{object_key}"
            logger.debug(f"✓ COS upload: {url}")
            return url
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"COS upload failed: {error_code} - {e}")
            raise
    
    async def _upload_to_cloudant_with_retry(
        self, 
        data: dict, 
        circuit_hash: str,
        attempt: int
    ) -> str:
        """Upload structured metadata to Cloudant database using ibmcloudant SDK"""
        # Generate document ID
        timestamp = data.get('timestamp', datetime.utcnow().isoformat())
        backend = data.get('backend', 'unknown')
        # Clean timestamp for use in doc ID
        clean_timestamp = (
            timestamp
            .replace(':', '-')
            .replace('.', '_')
            .replace('+', '_')
        )
        doc_id = f"heartbeat_{clean_timestamp}_{backend}"
        
        # Build document
        document = {
            '_id': doc_id,
            'type': 'heartbeat',
            'timestamp': timestamp,
            'backend': {
                'name': backend,
                'qubits': data.get('num_qubits', 5)
            },
            'job': {
                'id': data.get('job_id', ''),
                'shots': data.get('shots', 1024)
            },
            'circuit': {
                'hash': circuit_hash,
                'qubits_used': [96, 102, 103, 104]  # Cardiogram tetrad
            },
            'measurements': {
                'counts': data.get('counts', {}),
                'total_shots': data.get('shots', 1024),
                'unique_outcomes': len(data.get('counts', {}))
            },
            'topology': {
                'statistics': {
                    'mean_error': data.get('mean_qubit_error', 0),
                    'overall_error': data.get('overall_error', 0),
                    'error_variance': data.get('error_variance', 0),
                    'roughness': (
                        data.get('surface_data', {}).get('roughness', 0)
                    )
                },
                'qubit_errors': data.get('qubit_errors', [])
            },
            'metadata': {
                'created_at': datetime.utcnow().isoformat(),
                'upload_attempt': attempt + 1,
                'source_file': str(
                    Path(data.get('job_id', 'unknown'))
                )
            }
        }
        
        loop = asyncio.get_event_loop()
        
        try:
            result = await loop.run_in_executor(
                None,
                lambda: self.cloudant_client.post_document(
                    db=self.cloudant_db_name,
                    document=document
                ).get_result()
            )
            
            created_id = result.get('id', doc_id)
            logger.debug(f"✓ Cloudant doc: {created_id}")
            return created_id
            
        except ApiException as e:
            logger.error(f"Cloudant upload failed: {e.message}")
            raise
    
    def _hash_file(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file contents"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()[:16]  # First 16 chars
    
    def close(self):
        """Close cloud service connections"""
        # ibmcloudant SDK doesn't require explicit disconnect
        logger.info("Cloud service connections closed")


# Convenience function for synchronous usage
def upload_heartbeat_sync(file_path: Path) -> UploadResult:
    """
    Synchronous wrapper for upload_heartbeat
    
    Usage:
        result = upload_heartbeat_sync(Path("cardiogram.json"))
        if result.success:
            print(f"Uploaded: {result.cos_url}")
    """
    uploader = QuantumTopologyUploader()
    try:
        result = asyncio.run(uploader.upload_heartbeat(file_path))
        return result
    finally:
        uploader.close()
