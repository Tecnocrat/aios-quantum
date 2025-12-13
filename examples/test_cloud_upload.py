"""
Test IBM Cloud Connection

Quick test to verify COS and Cloudant credentials are working
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv

def test_cloud_object_storage():
    """Test COS connection"""
    print("\n🧪 Testing Cloud Object Storage...")
    
    import ibm_boto3
    from ibm_botocore.client import Config
    
    api_key = os.getenv('IBM_CLOUD_API_KEY')
    instance_id = os.getenv('COS_INSTANCE_ID')
    endpoint = os.getenv('COS_ENDPOINT')
    bucket = os.getenv('COS_BUCKET_NAME')
    
    if not all([api_key, instance_id, endpoint, bucket]):
        print("❌ Missing COS credentials in .env")
        print("   Required: IBM_CLOUD_API_KEY, COS_INSTANCE_ID, COS_ENDPOINT, COS_BUCKET_NAME")
        return False
    
    try:
        client = ibm_boto3.client(
            's3',
            ibm_api_key_id=api_key,
            ibm_service_instance_id=instance_id,
            config=Config(signature_version='oauth'),
            endpoint_url=endpoint
        )
        
        # List buckets
        response = client.list_buckets()
        buckets = [b['Name'] for b in response.get('Buckets', [])]
        
        print(f"✓ Connected to COS: {endpoint}")
        print(f"  Available buckets: {', '.join(buckets)}")
        
        if bucket in buckets:
            print(f"  ✓ Target bucket exists: {bucket}")
            
            # List objects
            objects = client.list_objects_v2(Bucket=bucket, MaxKeys=5)
            count = objects.get('KeyCount', 0)
            print(f"  ✓ Objects in bucket: {count}")
            
            if count > 0:
                print("  Sample objects:")
                for obj in objects.get('Contents', [])[:3]:
                    print(f"    - {obj['Key']} ({obj['Size']} bytes)")
        else:
            print(f"  ⚠️  Target bucket not found: {bucket}")
            print(f"     Create it in IBM Cloud Console first")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ COS connection failed: {e}")
        return False


def test_cloudant():
    """Test Cloudant connection using ibmcloudant SDK"""
    print("\n🧪 Testing Cloudant Database...")
    
    from ibmcloudant.cloudant_v1 import CloudantV1
    from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
    
    api_key = os.getenv('CLOUDANT_API_KEY')
    url = os.getenv('CLOUDANT_URL')
    db_name = os.getenv('CLOUDANT_DATABASE')
    
    if not all([api_key, url, db_name]):
        print("❌ Missing Cloudant credentials in .env")
        print("   Required: CLOUDANT_API_KEY, CLOUDANT_URL, CLOUDANT_DATABASE")
        return False
    
    try:
        # Create IAM authenticator
        authenticator = IAMAuthenticator(api_key)
        
        # Create Cloudant client
        client = CloudantV1(authenticator=authenticator)
        client.set_service_url(url)
        
        # List databases
        response = client.get_all_dbs()
        all_dbs = response.get_result()
        
        print(f"✓ Connected to Cloudant: {url}")
        print(f"  Available databases: {len(all_dbs)}")
        
        if db_name in all_dbs:
            print(f"  ✓ Target database exists: {db_name}")
            
            # Get database info
            response = client.get_database_information(db=db_name)
            info = response.get_result()
            doc_count = info.get('doc_count', 0)
            
            print(f"  ✓ Documents in database: {doc_count}")
            
            if doc_count > 0:
                print("  Sample documents:")
                response = client.post_all_docs(
                    db=db_name,
                    include_docs=False,
                    limit=3
                )
                result = response.get_result()
                for row in result.get('rows', []):
                    print(f"    - {row['id']}")
        else:
            print(f"  ⚠️  Target database not found: {db_name}")
            print(f"     Create it in Cloudant Dashboard first")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Cloudant connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_uploader():
    """Test the QuantumTopologyUploader class"""
    print("\n🧪 Testing QuantumTopologyUploader...")
    
    try:
        from aios_quantum.cloud.uploader import QuantumTopologyUploader
        
        uploader = QuantumTopologyUploader()
        
        print("✓ Uploader initialized successfully")
        print(f"  COS endpoint: {uploader.cos_endpoint}")
        print(f"  COS bucket: {uploader.cos_bucket}")
        print(f"  Cloudant database: {uploader.cloudant_db_name}")
        
        uploader.close()
        return True
        
    except Exception as e:
        print(f"❌ Uploader initialization failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("IBM CLOUD CONNECTION TEST")
    print("=" * 70)
    
    # Load environment
    load_dotenv()
    
    # Check credentials exist
    print("\n📋 Checking .env file...")
    required = [
        'IBM_CLOUD_API_KEY',
        'COS_INSTANCE_ID',
        'COS_ENDPOINT',
        'COS_BUCKET_NAME',
        'CLOUDANT_API_KEY',
        'CLOUDANT_URL',
        'CLOUDANT_DATABASE'
    ]
    
    missing = [key for key in required if not os.getenv(key)]
    
    if missing:
        print("❌ Missing environment variables:")
        for key in missing:
            print(f"   - {key}")
        print("\nPlease add them to your .env file")
        print("See: docs/IBM_CLOUD_SETUP_GUIDE.md")
        return False
    
    print("✓ All required credentials found in .env")
    
    # Run tests
    results = []
    results.append(("Cloud Object Storage", test_cloud_object_storage()))
    results.append(("Cloudant Database", test_cloudant()))
    results.append(("Uploader Module", test_uploader()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for name, success in results:
        status = "✓ PASS" if success else "❌ FAIL"
        print(f"{status:10} {name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🚀 All systems operational!")
        print("\nNext steps:")
        print("  1. Run: python examples/backfill_cloud_data.py")
        print("  2. Upload existing heartbeats to cloud")
        print("  3. Verify in IBM Cloud Console")
    else:
        print("\n⚠️  Some tests failed. Please check:")
        print("  1. IBM Cloud services are provisioned")
        print("  2. Service credentials are correct")
        print("  3. API keys have proper permissions")
        print("\nSee: docs/IBM_CLOUD_SETUP_GUIDE.md")
    
    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
