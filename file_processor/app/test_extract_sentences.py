"""
API endpoint để test extract sentences từ PDF và DOCX files
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import List, Dict, Any
import tempfile
import os
from pathlib import Path

from services.file_process_service import FileProcessService
from nlp.text_preprocess import (
    preprocess_pdf_text,
    normalize_full_text,
    extract_plagiarism_zone,
    extract_valid_sentences
)

router = APIRouter(tags=["test-extract"])


@router.post("/test/extract-sentences")
async def extract_sentences_from_file(
    file: UploadFile = File(...),
    min_words: int = Form(8),
    max_words: int = Form(200),
    language: str = Form("vi"),
    use_zone: bool = Form(False)
) -> Dict[str, Any]:
    """
    Extract và tiền xử lý câu từ PDF hoặc DOCX file
    
    Parameters:
    - file: PDF hoặc DOCX file
    - min_words: Số từ tối thiểu trong câu (default: 8)
    - max_words: Số từ tối đa trong câu (default: 200)
    - language: Ngôn ngữ (vi hoặc en, default: vi)
    - use_zone: Có cắt vùng plagiarism zone không (default: True)
    
    Returns:
    - List of extracted and cleaned sentences
    """
    
    # Kiểm tra file type
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in [".pdf", ".docx"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_extension}. Only .pdf and .docx are supported"
        )
    
    try:
        # Tạo temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Extract text dựa theo file type
        if file_extension == ".pdf":
            result = FileProcessService.extract_text_from_pdf(temp_file_path)
        else:  # .docx
            result = FileProcessService.extract_text_from_word(temp_file_path)
        
        # Xóa temp file
        os.unlink(temp_file_path)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=f"Failed to extract text: {result.get('error')}"
            )
        
        raw_text = result.get("text", "")
        
        if not raw_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No text content found in file"
            )
        
        # Tiền xử lý và extract sentences
        sentences = preprocess_pdf_text(
            raw_text=raw_text,
            language=language,
            min_words=min_words,
            max_words=max_words,
            use_zone=use_zone
        )
        
        return {
            "status": "success",
            "file_name": file.filename,
            "file_type": file_extension,
            "total_sentences": len(sentences),
            "sentences": sentences,
            "metadata": {
                "min_words": min_words,
                "max_words": max_words,
                "language": language,
                "use_zone": use_zone,
                "file_size": len(content),
                "original_text_length": len(raw_text)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )


@router.post("/test/extract-text-only")
async def extract_text_only(
    file: UploadFile = File(...)
) -> Dict[str, Any]:
    """
    Chỉ extract text (không tiền xử lý) từ PDF hoặc DOCX file
    
    Parameters:
    - file: PDF hoặc DOCX file
    
    Returns:
    - Raw text extracted from file
    """
    
    # Kiểm tra file type
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in [".pdf", ".docx"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_extension}. Only .pdf and .docx are supported"
        )
    
    try:
        # Tạo temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Extract text dựa theo file type
        if file_extension == ".pdf":
            result = FileProcessService.extract_text_from_pdf(temp_file_path)
        else:  # .docx
            result = FileProcessService.extract_text_from_word(temp_file_path)
        
        # Xóa temp file
        os.unlink(temp_file_path)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=f"Failed to extract text: {result.get('error')}"
            )
        
        return {
            "status": "success",
            "file_name": file.filename,
            "file_type": file_extension,
            "text": result.get("text", ""),
            "text_length": len(result.get("text", "")),
            "metadata": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )


@router.post("/test/extract-plagiarism-zone")
async def extract_plagiarism_zone_endpoint(
    file: UploadFile = File(...)
) -> Dict[str, Any]:
    """
    Extract only plagiarism zone (phần cần check) từ PDF hoặc DOCX file
    
    Parameters:
    - file: PDF hoặc DOCX file
    
    Returns:
    - Plagiarism zone text
    """
    
    # Kiểm tra file type
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in [".pdf", ".docx"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_extension}. Only .pdf and .docx are supported"
        )
    
    try:
        # Tạo temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Extract text dựa theo file type
        if file_extension == ".pdf":
            result = FileProcessService.extract_text_from_pdf(temp_file_path)
        else:  # .docx
            result = FileProcessService.extract_text_from_word(temp_file_path)
        
        # Xóa temp file
        os.unlink(temp_file_path)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=f"Failed to extract text: {result.get('error')}"
            )
        
        raw_text = result.get("text", "")
        
        # Normalize text
        normalized_text = normalize_full_text(raw_text)
        
        # Extract plagiarism zone
        plagiarism_zone = extract_plagiarism_zone(normalized_text)
        
        return {
            "status": "success",
            "file_name": file.filename,
            "file_type": file_extension,
            "original_text_length": len(raw_text),
            "normalized_text_length": len(normalized_text),
            "plagiarism_zone_length": len(plagiarism_zone),
            "plagiarism_zone": plagiarism_zone
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )


@router.post("/test/preprocess-text")
async def preprocess_text_endpoint(
    min_words: int = Form(8),
    max_words: int = Form(200),
    language: str = Form("vi"),
    use_zone: bool = Form(True),
    text: str = Form(...)
) -> Dict[str, Any]:
    """
    Tiền xử lý text trực tiếp (không upload file)
    
    Parameters:
    - text: Raw text content
    - min_words: Số từ tối thiểu trong câu (default: 8)
    - max_words: Số từ tối đa trong câu (default: 200)
    - language: Ngôn ngữ (vi hoặc en, default: vi)
    - use_zone: Có cắt vùng plagiarism zone không (default: True)
    
    Returns:
    - List of extracted and cleaned sentences
    """
    
    try:
        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail="Text content is empty"
            )
        
        # Tiền xử lý và extract sentences
        sentences = preprocess_pdf_text(
            raw_text=text,
            language=language,
            min_words=min_words,
            max_words=max_words,
            use_zone=use_zone
        )
        
        return {
            "status": "success",
            "total_sentences": len(sentences),
            "sentences": sentences,
            "metadata": {
                "min_words": min_words,
                "max_words": max_words,
                "language": language,
                "use_zone": use_zone,
                "input_text_length": len(text)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing text: {str(e)}"
        )
