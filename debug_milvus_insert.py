"""
Debug Milvus insert issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pymilvus import Collection, utility, connections
from db.milvus import connect_milvus
from service.document_service import DocumentService
import json

def debug_milvus_insert():
    """Debug why data not showing in Milvus"""
    
    try:
        # Connect to Milvus
        alias = connect_milvus()
        collection_name = "plagiarism_docs_2024"
        
        print(f"🔍 Debug Milvus Insert for: {collection_name}")
        print("=" * 50)
        
        # Check collection
        if utility.has_collection(collection_name, using=alias):
            print(f"✅ Collection exists")
            
            # Get collection
            collection = Collection(collection_name, using=alias)
            
            # Load collection (important!)
            print("📦 Loading collection...")
            collection.load()
            
            # Check count before
            num_before = collection.num_entities
            print(f"📊 Entities before: {num_before}")
            
            # Test insert with DocumentService
            print("\n🚀 Testing DocumentService insert...")
            doc_service = DocumentService()
            
            # Simple test
            test_text = "Machine learning là một nhánh của trí tuệ nhân tạo."
            test_metadata = {"test": True, "debug": True}
            
            result = doc_service.upload_document(
                text=test_text,
                subject_id=1,
                doc_id=888,
                metadata=test_metadata
            )
            
            print(f"✅ Upload result: {result}")
            
            # Flush to ensure data is written
            print("\n💾 Flushing data...")
            collection.flush()
            
            # Check count after
            num_after = collection.num_entities
            print(f"📊 Entities after: {num_after}")
            
            # Query to verify
            if num_after > 0:
                print("\n🔍 Querying inserted data...")
                results = collection.query(
                    expr="id >= 0",
                    output_fields=["id", "subject_id", "minhash", "content_vector"],
                    limit=5
                )
                
                print(f"📋 Found {len(results)} entities:")
                for i, result in enumerate(results):
                    print(f"\n   Entity {i+1}:")
                    print(f"   - ID: {result.get('id')}")
                    print(f"   - Subject ID: {result.get('subject_id')}")
                    print(f"   - MinHash: {result.get('minhash', 'None')[:30]}...")
                    
                    vector = result.get('content_vector', [])
                    if vector:
                        non_zero = sum(1 for v in vector if v != 0.0)
                        print(f"   - Vector: {len(vector)} dims, {non_zero} non-zero values")
                        print(f"   - Sample: {vector[:5]}...")
                    else:
                        print(f"   - Vector: Empty")
                        
            else:
                print("❌ No data found after insert")
                
        else:
            print(f"❌ Collection {collection_name} does not exist")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        connections.disconnect(alias)

if __name__ == "__main__":
    debug_milvus_insert()
