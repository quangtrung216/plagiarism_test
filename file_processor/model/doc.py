from pydantic import BaseModel

class DocUpResponse(BaseModel):
    document_id: str
    file_name: str
    subject_id: str
    file_path: str


class UploadBatchResponse(BaseModel):
    total: int
    succeeded: int
    failed: int
    documents: list[DocUpResponse]
    errors: list[dict]