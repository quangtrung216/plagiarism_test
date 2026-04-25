import io
from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from typing import List

from db.postgres import get_conn, release_conn
from model.check import Response
from repo_doc.doc_minhash import find_candidates_by_minhash
from services.embedding_service import embed_texts
from services.minhash import compute_minhash
from nlp.text_preprocess import preprocess_pdf_text
from services.check import run_plagiarism_check
from model.check import SentenceRecord

router = APIRouter()

ALLOWED_CONTENT_TYPES = {"application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
MINHASH_THRESHOLD = 0.05   # lọc thô: giữ tài liệu có Jaccard >= 5%


@router.post("/check",response_model=Response,summary="Kiểm tra đạo văn của tài liệu đẩy lên",)
async def check_plagiarism(
    subject_id: str = Form(..., description="ID môn học"),
    file: UploadFile = File(..., description="File PDF hoặc DOCX cần kiểm tra"),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận file PDF và DOCX")

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="File rỗng")

    # 1. Extract text từ file (PDF hoặc DOCX)
    try:
        import tempfile
        from pathlib import Path
        from services.file_process_service import FileProcessService

        # Determine file type and extension
        if file.content_type == "application/pdf":
            file_ext = ".pdf"
            file_type = "pdf"
        elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            file_ext = ".docx"
            file_type = "docx"
        else:
            raise HTTPException(status_code=400, detail="Loại file không được hỗ trợ")

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        extracted = FileProcessService.extract_text_from_file(tmp_path, file_type)
        Path(tmp_path).unlink(missing_ok=True)

        if not extracted.get("success"):
            raise HTTPException(status_code=400, detail=f"Lỗi trích xuất văn bản: {extracted.get('error')}")

        full_text = extracted.get("text", "")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý file: {str(e)}")

    # 2. Tiền xử lý và tách câu
    sentences = preprocess_pdf_text(
        raw_text=full_text,
        language="vi",
        min_words=8,
        max_words=200,
        use_zone=False,
    )

    if not sentences:
        raise HTTPException(status_code=400, detail="Không trích xuất được câu nào từ file")

    # 3. Tạo SentenceRecord list
    query_sentences = [
        SentenceRecord(sentence_index=i, text=s)
        for i, s in enumerate(sentences)
    ]

    # 4. Tính MinHash → lọc thô candidates
    minhash_values = compute_minhash(full_text)

    conn = await get_conn()
    try:
        candidates = await find_candidates_by_minhash(
            conn=conn,
            minhash=minhash_values,
            subject_id=subject_id,
            threshold=MINHASH_THRESHOLD,
        )
    finally:
        await release_conn(conn)

    # Không có tài liệu nào vượt ngưỡng lọc thô
    if not candidates:
        return Response(
            total_sentences=len(query_sentences),
            plagiarized_sentences=0,
            plagiarism_ratio=0.0,
            is_plagiarized=False,
            # sentence_labels=[0] * len(query_sentences),
            references=[],
        )

    # 5. Embedding các câu của tài liệu đẩy lên
    query_embeddings = embed_texts([s.text for s in query_sentences])

    # 6. So khớp chi tiết với từng tài liệu tham chiếu
    result = run_plagiarism_check(
        query_sentences=query_sentences,
        query_embeddings=query_embeddings,
        candidates=candidates,
    )

    return result
