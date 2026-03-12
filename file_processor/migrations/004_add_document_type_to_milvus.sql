-- Note: This is a reference for adding document_type field to Milvus collection
-- Milvus doesn't support ALTER TABLE like SQL, so we need to recreate the collection

-- Steps to add document_type field:
-- 1. Export existing data from plagiarism_sentences
-- 2. Drop the collection
-- 3. Recreate collection with new schema including document_type field
-- 4. Re-insert data with document_type values

-- New schema should include:
-- - id (Int64, PK, no auto_id)
-- - embedding (FloatVector, dim=1024)
-- - document_id (VarChar)
-- - sentence_id (VarChar) 
-- - text (VarChar)
-- - document_type (VarChar) -- NEW FIELD

-- Example recreation (run in Python with pymilvus):
"""
from pymilvus import Collection, FieldSchema, CollectionSchema, DataType, connections

# Connect to Milvus
connections.connect(alias="plagiarism_db", host="localhost", port=19530)

# Define new schema with document_type field
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024),
    FieldSchema(name="document_id", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="sentence_id", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="document_type", dtype=DataType.VARCHAR, max_length=100)  # NEW FIELD
]

schema = CollectionSchema(fields, "Plagiarism sentences with document type")

# Create new collection
collection = Collection("plagiarism_sentences_v2", schema, using="plagiarism_db")

# Create index
index_params = {
    "metric_type": "COSINE",
    "index_type": "HNSW",
    "params": {"M": 8, "efConstruction": 64}
}
collection.create_index("embedding", index_params)

print("Collection created with document_type field")
"""
