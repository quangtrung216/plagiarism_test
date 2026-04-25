from pydantic import BaseModel
from typing import Optional, List


class PreprocessRequest(BaseModel):
    text: str
    language: Optional[str] = "vi"
    min_words: Optional[int] = 8
    max_words: Optional[int] = 200
    use_zone: Optional[bool] = False


class PreprocessResponse(BaseModel):
    success: bool
    total_sentences: Optional[int] = None
    sentences: List[str] = []
    metadata: Optional[dict] = None
    error: Optional[str] = None


class AnalysisResponse(BaseModel):
    success: bool
    total_lines: Optional[int] = None
    total_paragraphs: Optional[int] = None
    total_characters: Optional[int] = None
    total_words: Optional[int] = None
    plagiarism_zone_length: Optional[int] = None
    plagiarism_zone_percentage: Optional[float] = None
    error: Optional[str] = None


class FileUploadProcessResponse(BaseModel):
    success: bool
    file_type: Optional[str] = None
    total_sentences: Optional[int] = None
    sentences: List[str] = []
    metadata: Optional[dict] = None
    error: Optional[str] = None
