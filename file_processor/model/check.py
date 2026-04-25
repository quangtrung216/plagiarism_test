from pydantic import BaseModel

class SentenceRecord(BaseModel):
    sentence_index: int
    text: str

class MatchedSementicUnit(BaseModel):
    query_sentence_index: int
    query_sentence_text: str
    query_page: int
    ref_sentence_text: str
    ref_page: int
    similarity: float

class ReferenceMatch(BaseModel):
    document_id: str
    file_name: str
    subject_id: str
    jaccard_similarity: float
    plagiarism_ratio: float
    plagiarized_count: int
    matched_sentences: list[MatchedSementicUnit]

class Response(BaseModel):
    total_sentences: int
    plagiarized_sentences: int
    plagiarism_ratio: float
    is_plagiarized: bool
    sentence_labels: list[int]
    references: list[ReferenceMatch]