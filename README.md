# Plagiarism Detection Project

This project detects plagiarism in uploaded documents.

## Project Structure

- [backend](backend/) - FastAPI backend service
- [frontend](frontend/) - Next.js frontend application
- [file_processor](file_processor/) - File processing service

## Luồng API (File Processor)

### Endpoint

`POST /check`

Được cài đặt tại: `file_processor/app/check_plagiarism.py` (hàm `check_plagiarism`).

### Request

Content-Type: `multipart/form-data`

Các trường:

- `subject_id` (string, bắt buộc): ID môn học.
- `file` (file, bắt buộc): Tài liệu cần kiểm tra.
  - Chỉ chấp nhận `content_type`:
    - `application/pdf`
    - `application/vnd.openxmlformats-officedocument.wordprocessingml.document` (DOCX)

### Sơ đồ luồng

```mermaid
flowchart TD
  Client[Client] --> API[FastAPI: check_plagiarism\nPOST /check (multipart/form-data)\nsubject_id + file]
  API --> Validate{Kiểm tra đầu vào\n- content_type (PDF/DOCX)\n- file không rỗng}

  Validate -->|Không hợp lệ| Err400A[HTTP 400\nSai loại file hoặc file rỗng]
  Validate -->|Hợp lệ| Extract[Trích xuất văn bản\nFileProcessService.extract_text_from_file]

  Extract -->|Thất bại| Err400B[HTTP 400\nLỗi trích xuất văn bản]
  Extract -->|Thành công| Split[Tiền xử lý + tách câu\npreprocess_pdf_text]

  Split -->|Không có câu| Err400C[HTTP 400\nKhông trích xuất được câu nào]
  Split -->|Có câu| Minhash[Tính MinHash\ncompute_minhash(full_text)]

  Minhash --> Query[Lọc candidates (Postgres)\nfind_candidates_by_minhash\nsubject_id + threshold 0.05]
  Query --> Cand{Có candidates?}

  Cand -->|Không có candidates| Zero[Response\n0% đạo văn\nreferences=[]]
  Cand -->|Có candidates| Embed[Embedding câu\nembed_texts]
  Embed --> Match[So khớp chi tiết\nrun_plagiarism_check]
  Match --> Res[Response\nmodel.check.Response]
```

### Các bước xử lý (tóm tắt)

1. Kiểm tra loại file (PDF/DOCX) và file không rỗng.
2. Trích xuất toàn bộ văn bản từ file qua `FileProcessService.extract_text_from_file`.
3. Tiền xử lý và tách câu bằng `preprocess_pdf_text` (tiếng Việt):
   - `min_words=8`
   - `max_words=200`
4. Tính MinHash từ `full_text` bằng `compute_minhash`.
5. Kết nối Postgres và lọc thô danh sách tài liệu tham chiếu theo:
   - `subject_id`
   - ngưỡng `MINHASH_THRESHOLD = 0.05`
   sử dụng `find_candidates_by_minhash`.
6. Nếu không có tài liệu nào vượt ngưỡng lọc thô: trả về kết quả 0% đạo văn.
7. Nếu có candidates: tạo embedding cho các câu bằng `embed_texts`.
8. So khớp chi tiết với từng tài liệu tham chiếu bằng `run_plagiarism_check`.
9. Trả về kết quả dạng `model.check.Response`.

### Response

Response thành công theo model: `model.check.Response`.

Khi không có candidates vượt ngưỡng lọc thô (MinHash), API trả về:

- `total_sentences`: số câu trích xuất được
- `plagiarized_sentences`: `0`
- `plagiarism_ratio`: `0.0`
- `is_plagiarized`: `false`
- `references`: `[]`

### Trường hợp lỗi

- `400`:
  - Không đúng loại file (không phải PDF/DOCX)
  - File rỗng
  - Trích xuất văn bản thất bại (`Lỗi trích xuất văn bản: ...`)
  - Không trích xuất được câu nào từ file
- `500`:
  - Lỗi ngoài dự kiến trong quá trình xử lý file (`Lỗi xử lý file: ...`)

