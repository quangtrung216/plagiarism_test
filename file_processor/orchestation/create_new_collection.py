#!/usr/bin/env python3
"""
Tạo collection mới với subject_id và document_type fields
Drop collection cũ (dữ liệu test) và tạo collection mới sạch
"""

import os
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from dotenv import load_dotenv

def create_new_collection():
    """Drop collection cũ và tạo collection mới với schema đầy đủ"""
    
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
        
        # Drop collection cũ nếu tồn tại
        if utility.has_collection(collection_name, using=alias):
            print(f"🗑️  Dropping old collection '{collection_name}'...")
            utility.drop_collection(collection_name, using=alias)
            print(f"✅ Dropped old collection")
        else:
            print(f"ℹ️  Collection '{collection_name}' does not exist, creating new one...")
        
        # Define schema mới với đầy đủ fields
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False, description="Primary key"),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768, description="Sentence embedding vector"),
            FieldSchema(name="document_id", dtype=DataType.VARCHAR, max_length=65535, description="Document ID"),
            FieldSchema(name="sentence_id", dtype=DataType.VARCHAR, max_length=65535, description="Sentence ID"),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535, description="Sentence text"),
            FieldSchema(name="subject_id", dtype=DataType.VARCHAR, max_length=100, description="Subject ID"),        # NEW
            FieldSchema(name="document_type", dtype=DataType.VARCHAR, max_length=100, description="Document type")  # NEW
        ]
        
        schema = CollectionSchema(fields, "Plagiarism sentences with metadata", consistency_level="Strong")
        
        # Tạo collection mới
        print(f"🏗️  Creating new collection '{collection_name}'...")
        collection = Collection(collection_name, schema, using=alias)
        print(f"✅ Created collection with {len(fields)} fields")
        
        # Tạo index cho embedding field
        print("🔍 Creating index for embedding field...")
        index_params = {
            "metric_type": "COSINE",
            "index_type": "HNSW",
            "params": {"M": 16, "efConstruction": 200}
        }
        collection.create_index("embedding", index_params)
        print("✅ Created HNSW index for embeddings")
        
        # Tạo scalar indexes cho fields mới
        print("🏷️  Creating scalar indexes...")
        collection.create_index("subject_id", index_type="STL_SORT")
        collection.create_index("document_type", index_type="STL_SORT")
        print("✅ Created scalar indexes for subject_id and document_type")
        
        # Show collection info
        print(f"\n📊 Collection Info:")
        print(f"   Name: {collection.name}")
        print(f"   Fields: {[field.name for field in collection.schema.fields]}")
        print(f"   Primary Key: {collection.primary_field.name}")
        print(f"   Entities: {collection.num_entities}")
        
        print(f"\n🎉 Collection '{collection_name}' created successfully!")
        print(f"   Ready for new data with subject_id and document_type fields!")
        
        return collection
        
    except Exception as e:
        print(f"❌ Error creating collection: {str(e)}")
        return None
    finally:
        try:
            connections.disconnect(alias)
        except:
            pass

def main():
    print("🚀 CREATE NEW COLLECTION (Clean Slate)")
    print("=" * 50)
    print("This will:")
    print("1. Drop old collection (test data)")
    print("2. Create new collection with subject_id & document_type")
    print("3. Create indexes for optimal performance")
    print()
    
    choice = input("Continue? (yes/no): ").strip().lower()
    if choice != 'yes':
        print("Operation cancelled.")
        return
    
    collection = create_new_collection()
    
    if collection:
        print("\n✨ Next steps:")
        print("1. Update worker to insert subject_id and document_type")
        print("2. Update check_service to use new fields for filtering")
        print("3. Upload new documents to test")
    else:
        print("\n❌ Failed to create collection!")

if __name__ == "__main__":
    main()
