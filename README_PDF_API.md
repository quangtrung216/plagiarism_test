# PDF Upload API with MinHash Integration

API để upload tài liệu PDF với tự động tiền xử lý, tạo MinHash bằng datasketch, tạo embeddings và lưu trữ metadata vào PostgreSQL.

## Tính năng

- **Upload PDF**: Nhận file PDF và xử lý tự động
- **Tiền xử lý text**: Tokenization, loại bỏ stopwords, xử lý tiếng Việt
- **MinHash Generation**: Tạo MinHash signatures với datasketch
- **Embeddings**: Tạo vector embeddings với sentence transformers
- **Lưu trữ**: Metadata trong PostgreSQL, vectors trong Milvus
- **Background Processing**: Xử lý bất đồng bộ cho performance
- **Status Tracking**: Theo dõi trạng thái xử lý tài liệu

## Cài đặt

```bash
# Install dependencies
pip install -r requirements.txt

# Khởi động các services cần thiết:
# - PostgreSQL (đã có schema trong db/schema.sql)
# - Milvus vector database
```

## Khởi động API

```bash
python api/pdf_upload_api.py
```

API sẽ chạy tại `http://localhost:8000`

## API Endpoints

### 1. Upload PDF

**POST** `/upload-pdf`

Upload file PDF để xử lý.

**Request:**
- `file`: PDF file (multipart/form-data)
- `title` (optional): Tiêu đề tài liệu
- `author` (optional): Tác giả
- `subject_id` (optional): ID môn học/khóa học (default: 1)
- `metadata` (optional): JSON string với additional metadata

**Response:**
```json
{
  "success": true,
  "message": "PDF uploaded successfully. Processing started in background.",
  "document_id": 123,
  "file_info": {
    "filename": "document.pdf",
    "size": 1048576,
    "pages": 10,
    "has_text": true
  }
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/upload-pdf" \
  -F "file=@document.pdf" \
  -F "title=Machine Learning Document" \
  -F "author=John Doe" \
  -F "subject_id=101" \
  -F 'metadata={"course": "AI101", "semester": "Fall 2023"}'
```

### 2. Check Document Status

**GET** `/document-status/{doc_id}`

Kiểm tra trạng thái xử lý của tài liệu.

**Response:**
```json
{
  "document_id": 123,
  "status": "completed",
  "total_sentences": 45,
  "processed_sentences": 42,
  "vector_count": 1,
  "error_message": null
}
```

**Status values:**
- `pending`: Chờ xử lý
- `processing`: Đang xử lý
- `completed`: Hoàn thành
- `failed`: Xử lý thất bại

### 3. Get Document Details

**GET** `/document/{doc_id}`

Lấy chi tiết thông tin tài liệu.

**Response:**
```json
{
  "document": {
    "id": 123,
    "file_name": "document.pdf",
    "title": "Machine Learning Document",
    "author": "John Doe",
    "upload_date": "2023-12-01T10:30:00Z",
    "processed_date": "2023-12-01T10:32:15Z",
    "status": "completed",
    "total_sentences": 45,
    "processed_sentences": 42,
    "embedding_dimension": 384,
    "vector_count": 1,
    "metadata": {
      "course": "AI101",
      "minhash_signature": "a1b2c3d4..."
    }
  },
  "sentences_count": 42,
  "sentences_sample": [...]
}
```

### 4. List Documents

**GET** `/documents`

Liệt kê các tài liệu đã upload.

**Query Parameters:**
- `status` (optional): Filter theo status (`pending`, `processing`, `completed`, `failed`)
- `limit` (optional): Số lượng kết quả (default: 50)
- `offset` (optional): Offset for pagination (default: 0)

**Response:**
```json
{
  "documents": [...],
  "total": 25,
  "limit": 50,
  "offset": 0
}
```

### 5. Health Check

**GET** `/health`

Kiểm tra trạng thái các services.

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "postgresql": "connected",
    "milvus": "connected",
    "pdf_processor": "ready",
    "minhash_processor": "ready",
    "embedding_model": "loaded"
  }
}
```

## Luồng xử lý

Khi PDF được upload, hệ thống sẽ thực hiện các bước sau:

1. **Validation**: Kiểm tra file PDF có hợp lệ không
2. **Database Record**: Tạo record trong PostgreSQL với status `pending`
3. **Background Processing**:
   - **PDF Extraction**: Trích xuất text từ PDF
   - **Text Preprocessing**: 
     - Tokenize sentences
     - Remove stopwords (Vietnamese)
     - Filter valid sentences
   - **MinHash Generation**: Tạo MinHash signature với datasketch
   - **Embedding Generation**: Tạo vector embeddings
   - **Storage**: 
     - Lưu vectors vào Milvus
     - Lưu sentences và metadata vào PostgreSQL
4. **Status Update**: Cập nhật status thành `completed` hoặc `failed`

## Database Schema

### PostgreSQL Tables

#### `documents`
- Metadata về tài liệu (file info, status, statistics)
- Liên kết với Milvus vectors

#### `sentences`
- Individual sentences từ tài liệu
- Original và processed text
- Page numbers, word counts
- Hash values cho deduplication

#### `plagiarism_checks`, `plagiarism_matches`
- Results từ plagiarism detection
- Similarity scores và match details

### Milvus Collection

#### `plagiarism_docs`
- Document embeddings
- MinHash signatures
- Metadata JSON
- Subject IDs cho filtering

## Demo & Testing

### Run Demo Script

```bash
python examples/pdf_upload_demo.py
```

Script sẽ:
1. Test health check
2. Upload sample document
3. Monitor processing status
4. Retrieve document details
5. List all documents

### Manual Testing

```bash
# 1. Start API server
python api/pdf_upload_api.py

# 2. Test health
curl http://localhost:8000/health

# 3. Upload PDF
curl -X POST http://localhost:8000/upload-pdf \
  -F "file=@your_document.pdf" \
  -F "title=Test Document"

# 4. Check status (sử dụng document_id từ bước 3)
curl http://localhost:8000/document-status/123

# 5. Get details
curl http://localhost:8000/document/123
```

## Configuration

### Environment Variables

```bash
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=plagiarism_detection
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

# Milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_ALIAS=default

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

### MinHash Parameters

- `num_perm`: 128 permutations (balance accuracy vs performance)
- `threshold`: 0.8 similarity threshold
- `shingle_size`: 2-grams cho Vietnamese text

## Performance Considerations

### File Size Limits
- Recommended: < 50MB per PDF
- Large files: Consider chunking or preprocessing

### Processing Time
- Small PDF (< 10 pages): ~10-30 seconds
- Medium PDF (10-50 pages): ~30-120 seconds
- Large PDF (> 50 pages): ~2-5 minutes

### Scaling
- Background processing cho non-blocking uploads
- Batch processing cho multiple files
- Connection pooling cho database

## Error Handling

### Common Errors

1. **Invalid PDF**: File không phải PDF hoặc corrupted
2. **No Text Extracted**: PDF không có text có thể trích xuất
3. **Processing Failed**: Lỗi trong pipeline processing
4. **Database Error**: Connection hoặc storage issues

### Error Response Format

```json
{
  "success": false,
  "error": "Detailed error message"
}
```

## Monitoring & Logging

- API logs với uvicorn
- Database transaction logs
- Processing status tracking
- Error reporting và alerting

## Security Considerations

- File type validation (PDF only)
- File size limits
- Temporary file cleanup
- Input sanitization
- Rate limiting (recommended)

## Next Steps

1. **Enhanced Processing**: Support cho DOCX, TXT files
2. **Batch Operations**: Upload multiple files
3. **Advanced Search**: Semantic search với MinHash filtering
4. **User Management**: Authentication và authorization
5. **Performance Optimization**: Caching, queueing system
6. **Monitoring**: Metrics, alerts, dashboard

## Troubleshooting

### Common Issues

1. **API won't start**: Check dependencies và database connections
2. **Processing stuck**: Check background tasks và resource usage
3. **Database errors**: Verify schema và permissions
4. **Milvus connection**: Check vector database status

### Debug Mode

```bash
# Run with debug logging
uvicorn api.pdf_upload_api:app --reload --log-level debug
```

## Integration Examples

### Python Client

```python
import requests

# Upload PDF
with open("document.pdf", "rb") as f:
    files = {"file": f}
    data = {"title": "My Document"}
    response = requests.post("http://localhost:8000/upload-pdf", files=files, data=data)
    doc_id = response.json()["document_id"]

# Check status
status = requests.get(f"http://localhost:8000/document-status/{doc_id}")
print(status.json())
```

### JavaScript Client

```javascript
// Upload PDF
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('title', 'My Document');

fetch('http://localhost:8000/upload-pdf', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```
