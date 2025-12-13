"""
Backfill Cloud Data

Upload existing local heartbeat files to IBM Cloud services
"""

import asyncio
import sys
from pathlib import Path
from typing import List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aios_quantum.cloud.uploader import QuantumTopologyUploader, UploadResult


async def backfill_heartbeats(data_dir: Path) -> List[UploadResult]:
    """Upload all existing heartbeat files to cloud"""
    
    # Find heartbeat files
    patterns = [
        "cardiogram_real_*.json",
        "real_beat_*.json"
    ]
    
    files = []
    for pattern in patterns:
        files.extend(data_dir.glob(pattern))
    
    if not files:
        print(f"❌ No heartbeat files found in {data_dir}")
        return []
    
    print(f"\n📦 Found {len(files)} heartbeat file(s) to upload:")
    for f in files:
        print(f"   • {f.name}")
    
    # Initialize uploader
    uploader = QuantumTopologyUploader()
    
    # Upload each file
    results = []
    print(f"\n⬆️  Uploading to IBM Cloud...")
    
    for i, file_path in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] {file_path.name}")
        
        try:
            result = await uploader.upload_heartbeat(file_path)
            results.append(result)
            
            if result.success:
                if result.cos_url:
                    print(f"  ✓ COS: {result.cos_url}")
                if result.cloudant_id:
                    print(f"  ✓ Cloudant: {result.cloudant_id}")
                if result.errors:
                    for error in result.errors:
                        print(f"  ⚠️  {error}")
            else:
                print(f"  ❌ Upload failed")
                for error in result.errors:
                    print(f"     {error}")
                    
        except Exception as e:
            print(f"  ❌ Exception: {e}")
            results.append(UploadResult(success=False, errors=[str(e)]))
    
    uploader.close()
    return results


async def upload_surface_data(data_dir: Path, uploader: QuantumTopologyUploader):
    """Upload hypersphere surface files"""
    surface_files = list(data_dir.glob("hypersphere_surface_*.json"))
    
    if not surface_files:
        print("ℹ️  No hypersphere surface files to upload")
        return
    
    print(f"\n🌐 Found {len(surface_files)} surface file(s):")
    for f in surface_files:
        print(f"   • {f.name}")
    
    # For now, just log them
    # TODO: Implement surface-specific upload logic
    print("   (Surface upload not yet implemented)")


def print_summary(results: List[UploadResult]):
    """Print upload summary"""
    print("\n" + "=" * 70)
    print("UPLOAD SUMMARY")
    print("=" * 70)
    
    total = len(results)
    successful = sum(1 for r in results if r.success)
    failed = total - successful
    
    cos_uploads = sum(1 for r in results if r.cos_url)
    cloudant_uploads = sum(1 for r in results if r.cloudant_id)
    
    print(f"\nTotal files:        {total}")
    print(f"  ✓ Successful:     {successful}")
    print(f"  ❌ Failed:         {failed}")
    print(f"\nService uploads:")
    print(f"  COS:              {cos_uploads}/{total}")
    print(f"  Cloudant:         {cloudant_uploads}/{total}")
    
    # Calculate total size
    total_errors = sum(len(r.errors) for r in results if r.errors)
    if total_errors > 0:
        print(f"\n⚠️  Total errors: {total_errors}")
        print("   Check logs above for details")
    
    if successful > 0:
        print("\n🎉 Data successfully uploaded to IBM Cloud!")
        print("\n📊 View your data:")
        print("   • COS: https://cloud.ibm.com/objectstorage")
        print("   • Cloudant: https://cloud.ibm.com/cloudant")
        print("\n🔍 Query example (Python):")
        print("""
from cloudant.client import Cloudant
import os

client = Cloudant.iam(
    account_name=os.getenv('CLOUDANT_ACCOUNT'),
    api_key=os.getenv('CLOUDANT_API_KEY'),
    connect=True
)

db = client['quantum_topology']
result = db.get_query_result(
    selector={'type': 'heartbeat'},
    sort=[{'timestamp': 'desc'}]
)

for doc in result:
    print(f"{doc['timestamp']}: {doc['backend']['name']}")
        """)
    
    if failed > 0:
        print("\n⚠️  Some uploads failed. Possible causes:")
        print("   1. Network connectivity issues")
        print("   2. Invalid credentials (check .env)")
        print("   3. Bucket/database doesn't exist")
        print("   4. Insufficient permissions")
        print("\nRe-run this script to retry failed uploads")


async def main():
    """Main backfill operation"""
    print("=" * 70)
    print("IBM CLOUD DATA BACKFILL")
    print("=" * 70)
    print("\nThis script uploads existing local heartbeat data to IBM Cloud")
    print("Services: Cloud Object Storage + Cloudant Database")
    
    # Find data directory
    data_dir = Path(__file__).parent.parent / "cardiogram_results"
    
    if not data_dir.exists():
        print(f"\n❌ Data directory not found: {data_dir}")
        print("   Expected location: c:\\dev\\aios-quantum\\cardiogram_results")
        return False
    
    print(f"\n📂 Scanning: {data_dir}")
    
    # Upload heartbeats
    results = await backfill_heartbeats(data_dir)
    
    # Print summary
    print_summary(results)
    
    return len([r for r in results if r.success]) > 0


if __name__ == '__main__':
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Upload interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
