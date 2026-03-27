"""
Script to fix Milvus collection schema issues
"""

from pymilvus import utility, connections
from db.milvus import connect_milvus

def fix_milvus_collection():
    """Fix Milvus collection by dropping and recreating"""
    
    # Connect to Milvus
    alias = connect_milvus()
    
    collections_to_drop = ["plagiarism_docs", "plagiarism_docs_v2", "plagiarism_docs_2024"]
    
    try:
        for collection_name in collections_to_drop:
            # Check if collection exists
            if utility.has_collection(collection_name, using=alias):
                print(f"Collection '{collection_name}' exists, dropping it...")
                utility.drop_collection(collection_name, using=alias)
                print(f"Dropped collection '{collection_name}'")
            else:
                print(f"Collection '{collection_name}' does not exist")
        
        # List all collections
        collections = utility.list_collections(using=alias)
        print(f"Remaining collections: {collections}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Disconnect
        connections.disconnect(alias)

if __name__ == "__main__":
    fix_milvus_collection()
