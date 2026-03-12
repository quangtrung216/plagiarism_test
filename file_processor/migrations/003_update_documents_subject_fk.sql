-- Add foreign key constraint for subject_id
-- First, make sure existing subject_id values exist in subjects table
-- Insert any missing subject_id from documents into subjects table
INSERT INTO subjects (subject_id, subject_name, description)
SELECT DISTINCT subject_id, subject_id, 'Auto-generated from existing data'
FROM documents 
WHERE subject_id IS NOT NULL 
AND subject_id NOT IN (SELECT subject_id FROM subjects)
ON CONFLICT (subject_id) DO NOTHING;

-- Add foreign key constraint
ALTER TABLE documents 
ADD CONSTRAINT fk_documents_subject 
FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) 
ON DELETE SET NULL ON UPDATE CASCADE;

-- Update index for better performance
CREATE INDEX IF NOT EXISTS idx_documents_subject_id_fk ON documents(subject_id);
