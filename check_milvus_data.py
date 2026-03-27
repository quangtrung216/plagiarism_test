"""
Script to check data in Milvus collection
"""

from pymilvus import Collection, utility, connections
from db.milvus import connect_milvus

def check_milvus_data():
    """Check data in Milvus collection"""
    
    try:
        # Connect to Milvus
        alias = connect_milvus()
        
        collection_name = "plagiarism_docs_2024"
        
        print(f"🔍 Checking Milvus collection: {collection_name}")
        print("=" * 50)
        
        # Check if collection exists
        if utility.has_collection(collection_name, using=alias):
            print(f"✅ Collection '{collection_name}' exists")
            
            # Get collection
            collection = Collection(collection_name, using=alias)
            collection.load()
            
            # Get collection info
            print(f"📊 Collection info:")
            print(f"   - Name: {collection.name}")
            print(f"   - Description: {collection.description}")
            print(f"   - Schema: {collection.schema}")
            
            # Get number of entities
            num_entities = collection.num_entities
            print(f"   - Total entities: {num_entities}")
            
            if num_entities > 0:
                print(f"\n📋 Sample data (first 5 entities):")
                
                # Query first 5 entities
                results = collection.query(
                    expr="id >= 0",
                    output_fields=["id", "subject_id", "minhash", "content_vector"],
                    limit=5
                )
                
                for i, result in enumerate(results):
                    print(f"\n   Entity {i+1}:")
                    print(f"   - ID: {result.get('id')}")
                    print(f"   - Subject ID: {result.get('subject_id')}")
                    print(f"   - MinHash: {result.get('minhash')[:50]}..." if result.get('minhash') else "   - MinHash: None")
                    print(f"   - Vector length: {len(result.get('content_vector', []))}")
                
                print(f"\n🎯 Milvus has {num_entities} document vectors!")
                
            else:
                print(f"\n❌ No data found in collection")
                
        else:
            print(f"❌ Collection '{collection_name}' does not exist")
            
            # List all collections
            collections = utility.list_collections(using=alias)
            print(f"\n📋 Available collections: {collections}")
        
    except Exception as e:
        print(f"❌ Error checking Milvus: {e}")
    
    finally:
        # Disconnect
        connections.disconnect(alias)

if __name__ == "__main__":
    check_milvus_data()
