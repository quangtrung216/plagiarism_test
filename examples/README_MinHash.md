# MinHash Integration with Datasketch

This document explains how to use the MinHash functionality integrated with the datasketch library for plagiarism detection.

## Overview

The MinHash integration provides:
- **Fast similarity detection**: MinHash signatures for quick filtering of similar documents
- **Scalable processing**: Efficient computation for large document collections
- **Integration with embeddings**: Combined MinHash and vector embeddings for accurate similarity detection

## Key Components

### 1. MinHashProcessor (`text_process/minhash_processor.py`)

Handles MinHash generation and similarity computation:

```python
from text_process.minhash_processor import MinHashProcessor

# Initialize processor
processor = MinHashProcessor(num_perm=128, threshold=0.8)

# Create MinHash signature
signature = processor.get_minhash_signature("document text here")

# Calculate similarity
similarity = processor.calculate_similarity(text1, text2)
```

### 2. DocumentService (`service/document_service.py`)

High-level service for document upload and search:

```python
from service.document_service import DocumentService

# Initialize service
doc_service = DocumentService()

# Upload document
result = doc_service.upload_document(
    text="document content",
    subject_id=101,
    doc_id=1,
    metadata={"title": "My Document"}
)

# Search similar documents
similar = doc_service.find_similar_documents(query_text="search query")
```

## Installation

Install the required dependencies:

```bash
pip install datasketch>=1.6.4
```

The dependency is already added to `requirements.txt`.

## Usage Examples

### Basic Document Upload

```python
from service.document_service import DocumentService

# Initialize service
doc_service = DocumentService()

# Upload a single document
result = doc_service.upload_document(
    text="This is the document content to analyze for plagiarism.",
    subject_id=101,  # Course/department ID
    doc_id=1,        # Unique document ID
    metadata={"title": "Sample Document", "author": "John Doe"}
)

print(f"MinHash signature: {result['processed_doc']['minhash_signature']}")
```

### Chunk-based Upload

For longer documents, you can upload as chunks:

```python
# Upload document as chunks (recommended for long documents)
chunk_result = doc_service.upload_document_chunks(
    text="Long document content...",
    subject_id=101,
    doc_id=2,
    chunk_size=5,  # 5 sentences per chunk
    metadata={"title": "Long Document"}
)

print(f"Uploaded {chunk_result['num_chunks']} chunks")
```

### Similarity Search

```python
# Find similar documents
similar_docs = doc_service.find_similar_documents(
    query_text="Text to search for similarities",
    subject_id=101,  # Optional: filter by subject
    limit=10,        # Maximum results
    similarity_threshold=0.7  # Minimum similarity
)

for doc in similar_docs:
    print(f"Doc ID: {doc['doc_id']}, Similarity: {doc['similarity']:.3f}")
```

### Direct MinHash Processing

```python
from text_process.minhash_processor import MinHashProcessor

processor = MinHashProcessor()

# Process document for upload
processed = processor.process_document_for_upload(
    text="Document content",
    doc_id="doc_123"
)

print(f"Signature: {processed['minhash_signature']}")
print(f"Sentences: {len(processed['processed_sentences'])}")
print(f"Stats: {processed['stats']}")
```

## Configuration Parameters

### MinHashProcessor Parameters

- `num_perm`: Number of permutations (default: 128)
  - Higher values = more accurate but slower
  - Typical range: 64-256

- `threshold`: Similarity threshold (default: 0.8)
  - Minimum similarity for LSH indexing
  - Range: 0.0-1.0

- `min_words`: Minimum words per sentence (default: 8)
  - Filters out short sentences

### DocumentService Parameters

- `model_name`: Sentence transformer model
  - Default: "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
  - Supports multilingual text including Vietnamese

- `embedding_dim`: Embedding dimension (default: 384)
  - Must match the selected model

- `collection_name`: Milvus collection name
  - Default: "plagiarism_docs"

## Database Schema

The Milvus collection includes these fields:

- `id`: Document/chunk ID (INT64, primary key)
- `subject_id`: Subject ID for filtering (INT64)
- `minhash`: MinHash signature (VARCHAR, 64 chars)
- `content_vector`: Embedding vector (FLOAT_VECTOR)
- `metadata`: Additional metadata (JSON)

## Performance Considerations

### MinHash vs Full Embeddings

1. **MinHash**: Fast filtering, low storage
   - Use for initial similarity screening
   - Quick to compute and compare
   - Good for large-scale filtering

2. **Embeddings**: Accurate similarity, higher computation
   - Use for final similarity scoring
   - Captures semantic meaning
   - Better for fine-grained similarity

### Recommended Workflow

1. **Upload**: Generate both MinHash and embeddings
2. **Search**: Use MinHash for initial filtering, then embeddings for ranking
3. **Storage**: Store both in Milvus for flexible querying

### Chunking Strategy

For long documents:
- Use 3-10 sentences per chunk
- Overlap chunks for better coverage
- Store both document-level and chunk-level signatures

## Example Output

When uploading a document, you get:

```python
{
    'doc_id': 1,
    'insert_result': <MilvusInsertResult>,
    'processed_doc': {
        'minhash_signature': 'a1b2c3d4e5f6...',
        'document_embedding': [0.1, 0.2, ...],
        'processed_sentences': ['cleaned sentence 1', ...],
        'stats': {
            'total_sentences': 5,
            'final_sentences': 4,
            'filtered_sentences': 1
        },
        'metadata': {...}
    },
    'collection_name': 'plagiarism_docs'
}
```

## Troubleshooting

### Common Issues

1. **Import Error**: Install datasketch
   ```bash
   pip install datasketch>=1.6.4
   ```

2. **Memory Issues**: Reduce `num_perm` or chunk size
3. **Slow Performance**: Use smaller embedding models or reduce chunk size

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Next Steps

1. Run the example: `python examples/minhash_upload_example.py`
2. Test with your own documents
3. Adjust parameters based on your use case
4. Integrate with your upload pipeline
