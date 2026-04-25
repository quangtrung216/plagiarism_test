from fastapi import APIRouter, HTTPException, File, UploadFile
from typing import List, Optional
from services.preprocess_service import PreprocessService
from services.file_process_service import FileProcessService
from model.preprocess import PreprocessRequest, PreprocessResponse, AnalysisResponse, FileUploadProcessResponse
import tempfile
from pathlib import Path

router = APIRouter(tags=["preprocess"])

@router.post("/preprocess/text", response_model=PreprocessResponse)
async def preprocess_text(request: PreprocessRequest):
    result = PreprocessService.preprocess_text(
        text=request.text,
        language=request.language,
        min_words=request.min_words,
        max_words=request.max_words,
        use_zone=request.use_zone
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Processing failed"))
    
    return result

@router.post("/preprocess/analyze", response_model=AnalysisResponse)
async def analyze_text_structure(request: PreprocessRequest):
    result = PreprocessService.analyze_text_structure(request.text)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Analysis failed"))
    
    return result

@router.post("/preprocess/batch", response_model=list)
async def preprocess_batch(requests: List[PreprocessRequest]):
    """
    Preprocess multiple texts in batch
    
    Process multiple texts in a single request
    """
    results = []
    for req in requests:
        result = PreprocessService.preprocess_text(
            text=req.text,
            language=req.language,
            min_words=req.min_words,
            max_words=req.max_words,
            use_zone=req.use_zone
        )
        results.append(result)
    
    return results

@router.get("/preprocess/info")
async def get_preprocess_info():
    """
    Get information about preprocessing settings and behavior
    """
    return {
        "description": "Text preprocessing service for plagiarism detection",
        "features": [
            "Extract valid sentences from raw text",
            "Support Vietnamese and English languages",
            "Automatic plagiarism zone detection",
            "Filter sentences by word count",
            "Remove citation sentences",
            "Normalize text and handle special characters"
        ],
        "excluded_sections": [
            "Cover page (bìa)",
            "Table of contents (mục lục)",
            "Acknowledgments (lời cảm ơn)",
            "List of tables/figures (danh mục bảng biểu)",
            "References (tài liệu tham khảo)",
            "Appendix (phụ lục)"
        ],
        "default_settings": {
            "language": "vi",
            "min_words": 8,
            "max_words": 200,
            "use_zone": False
        }
    }

@router.post("/preprocess/upload", response_model=FileUploadProcessResponse)
async def upload_and_process_file(
    file: UploadFile = File(...),
    language: Optional[str] = "vi",
    min_words: Optional[int] = 8,
    max_words: Optional[int] = 200,
    use_zone: Optional[bool] = False
):

    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing uploaded filename")

    # Validate file
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in [".pdf", ".docx"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Supported: .pdf, .docx"
        )
    
    tmp_path = None
    # Save file to temporary location
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Process file
        result = FileProcessService.process_file_and_extract_sentences(
            file_path=tmp_path,
            language=language,
            min_words=min_words,
            max_words=max_words,
            use_zone=use_zone,
            file_type="pdf" if file_ext == ".pdf" else "docx"
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Processing failed"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    finally:
        # Clean up temporary file
        try:
            if tmp_path:
                Path(tmp_path).unlink(missing_ok=True)
        except TypeError:
            if tmp_path and Path(tmp_path).exists():
                Path(tmp_path).unlink()
        except Exception:
            pass
