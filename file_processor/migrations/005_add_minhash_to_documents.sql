-- Add minhash field to documents table
ALTER TABLE documents
ADD COLUMN IF NOT EXISTS minhash INTEGER[];

-- Create index for faster queries on minhash
CREATE INDEX IF NOT EXISTS idx_documents_minhash ON documents USING GIN (minhash);
