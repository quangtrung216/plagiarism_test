-- Add subject_id and document_type to documents table
ALTER TABLE documents
ADD COLUMN IF NOT EXISTS subject_id VARCHAR(100),
ADD COLUMN IF NOT EXISTS document_type VARCHAR(50) DEFAULT 'none';

-- Optional: create indexes for faster filtering
CREATE INDEX IF NOT EXISTS idx_documents_subject_id ON documents(subject_id);
CREATE INDEX IF NOT EXISTS idx_documents_document_type ON documents(document_type);
CREATE INDEX IF NOT EXISTS idx_documents_subject_document ON documents(subject_id, document_type);


select * from subjects;
