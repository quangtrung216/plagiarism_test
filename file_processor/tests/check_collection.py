#!/usr/bin/env python3
"""
Kiểm tra schema của collection Milvus
"""

import os
from pymilvus import connections, Collection, utility
from dotenv import load_dotenv

def check_collection():
    """Kiểm tra schema và thông tin collection"""
    
    load_dotenv()
    alias = "default"  # Use default alias like milvus.py
    collection_name = "plagiarism_sentences"
    
    try:
        print(f"🔌 Connecting to Milvus...")
        connections.connect(
            alias=alias, 
            host=os.getenv("MILVUS_HOST", "localhost"),  # Use localhost - working config
            port=int(os.getenv("MILVUS_PORT", "19530"))
            # Use default database (no db_name parameter)
        )
        
        # Kiểm tra collection tồn tại
        if not utility.has_collection(collection_name, using=alias):
            print(f"❌ Collection '{collection_name}' does not exist!")
            return
        
        collection = Collection(collection_name, using=alias)
        
        print(f"\n📋 Collection: {collection_name}")
        print(f"   Total entities: {collection.num_entities}")
        print(f"   Primary key: {collection.primary_field.name}")
        
        print(f"\n🏗️  Schema fields:")
        for field in collection.schema.fields:
            field_info = {
                "name": field.name,
                "type": str(field.dtype),
                "is_primary": field.is_primary,
                "auto_id": field.auto_id if hasattr(field, 'auto_id') else False,
                "max_length": getattr(field, 'max_length', None),
                "dim": getattr(field, 'params', {}).get('dim', None),
                "description": getattr(field, 'description', '')
            }
            print(f"   - {field_info}")
        
        print(f"\n🔍 Indexes:")
        for index in collection.indexes:
            # Compatible with different PyMilvus versions
            index_info = {
                "name": getattr(index, 'index_name', 'unknown'),
                "field": getattr(index, 'field_name', 'unknown'),
                "type": getattr(index, 'index_type', getattr(index, 'params', {}).get('index_type', 'unknown')),
                "params": getattr(index, 'params', {})
            }
            print(f"   - {index_info}")
        
        print(f"\n📂 Partitions:")
        partitions = collection.partitions
        for partition in partitions:
            print(f"   - {partition.name}: {partition.num_entities} entities")
        
        # Kiểm tra xem có đủ fields mới không
        field_names = [field.name for field in collection.schema.fields]
        required_fields = ["subject_id", "document_type"]
        
        print(f"\n✅ Field Check:")
        for field in required_fields:
            if field in field_names:
                print(f"   ✅ {field}: PRESENT")
            else:
                print(f"   ❌ {field}: MISSING")
        
        if all(field in field_names for field in required_fields):
            print(f"\n🎉 Collection has all required fields!")
            print(f"   Ready for production use!")
        else:
            print(f"\n⚠️  Collection missing some fields!")
            print(f"   Need to recreate collection!")
        
    except Exception as e:
        print(f"❌ Error checking collection: {str(e)}")
    finally:
        try:
            connections.disconnect(alias)
        except:
            pass

def main():
    print("🔍 COLLECTION SCHEMA CHECKER")
    print("=" * 40)
    check_collection()

if __name__ == "__main__":
    main()
