-- PostgreSQL schema for plagiarism detection system
-- Contains tables for document metadata, sentences, and plagiarism results

-- Documents table - stores metadata about processed documents
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT,
    file_type VARCHAR(50) NOT NULL, -- 'pdf', 'txt', 'docx', etc.
    title TEXT,
    author VARCHAR(255),
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_date TIMESTAMP WITH TIME ZONE,
    total_sentences INTEGER DEFAULT 0,
    processed_sentences INTEGER DEFAULT 0,
    embedding_dimension INTEGER DEFAULT 0,
    vector_count INTEGER DEFAULT 0, -- Number of vectors stored in Milvus
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    error_message TEXT,
    metadata JSONB, -- Additional document metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Sentences table - stores individual sentences from documents
CREATE TABLE IF NOT EXISTS sentences (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    sentence_index INTEGER NOT NULL, -- Position in the original document
    original_sentence TEXT NOT NULL,
    processed_sentence TEXT NOT NULL, -- After preprocessing (stopword removal, etc.)
    word_count INTEGER NOT NULL,
    character_count INTEGER NOT NULL,
    page_number INTEGER, -- For PDFs
    paragraph_number INTEGER,
    sentence_hash VARCHAR(64) UNIQUE, -- For duplicate detection
    embedding_vector_id VARCHAR(255), -- Reference to Milvus vector ID
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Plagiarism checks table - stores plagiarism detection results
CREATE TABLE IF NOT EXISTS plagiarism_checks (
    id SERIAL PRIMARY KEY,
    query_document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    check_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    similarity_threshold DECIMAL(3,2) DEFAULT 0.70,
    total_comparisons INTEGER DEFAULT 0,
    potential_matches INTEGER DEFAULT 0,
    max_similarity_score DECIMAL(5,4),
    average_similarity_score DECIMAL(5,4),
    status VARCHAR(50) DEFAULT 'completed',
    processing_time_seconds INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Plagiarism matches table - stores individual sentence matches
CREATE TABLE IF NOT EXISTS plagiarism_matches (
    id SERIAL PRIMARY KEY,
    plagiarism_check_id INTEGER REFERENCES plagiarism_checks(id) ON DELETE CASCADE,
    query_sentence_id INTEGER REFERENCES sentences(id) ON DELETE CASCADE,
    matched_document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    matched_sentence_id INTEGER REFERENCES sentences(id) ON DELETE CASCADE,
    similarity_score DECIMAL(5,4) NOT NULL,
    match_type VARCHAR(50) DEFAULT 'exact', -- 'exact', 'paraphrase', 'partial'
    highlighted_query_sentence TEXT, -- Query sentence with highlighting
    highlighted_matched_sentence TEXT, -- Matched sentence with highlighting
    context_before_query TEXT, -- Context before query sentence
    context_after_query TEXT, -- Context after query sentence
    context_before_matched TEXT, -- Context before matched sentence
    context_after_matched TEXT, -- Context after matched sentence
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Document collections table - for organizing documents into collections
CREATE TABLE IF NOT EXISTS document_collections (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Document collection membership table
CREATE TABLE IF NOT EXISTS document_collection_members (
    id SERIAL PRIMARY KEY,
    collection_id INTEGER REFERENCES document_collections(id) ON DELETE CASCADE,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    added_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(collection_id, document_id)
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_documents_file_name ON documents(file_name);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_upload_date ON documents(upload_date);
CREATE INDEX IF NOT EXISTS idx_sentences_document_id ON sentences(document_id);
CREATE INDEX IF NOT EXISTS idx_sentences_sentence_hash ON sentences(sentence_hash);
CREATE INDEX IF NOT EXISTS idx_plagiarism_checks_query_document ON plagiarism_checks(query_document_id);
CREATE INDEX IF NOT EXISTS idx_plagiarism_matches_check_id ON plagiarism_matches(plagiarism_check_id);
CREATE INDEX IF NOT EXISTS idx_plagiarism_matches_query_sentence ON plagiarism_matches(query_sentence_id);
CREATE INDEX IF NOT EXISTS idx_plagiarism_matches_matched_document ON plagiarism_matches(matched_document_id);
CREATE INDEX IF NOT EXISTS idx_plagiarism_matches_similarity ON plagiarism_matches(similarity_score);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_document_collections_updated_at BEFORE UPDATE ON document_collections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Views for common queries
CREATE OR REPLACE VIEW document_statistics AS
SELECT 
    d.id,
    d.file_name,
    d.total_sentences,
    d.processed_sentences,
    d.vector_count,
    d.status,
    d.upload_date,
    d.processed_date,
    COUNT(s.id) as stored_sentences,
    AVG(s.word_count) as avg_sentence_length,
    MAX(s.word_count) as max_sentence_length
FROM documents d
LEFT JOIN sentences s ON d.id = s.document_id
GROUP BY d.id, d.file_name, d.total_sentences, d.processed_sentences, d.vector_count, d.status, d.upload_date, d.processed_date;

CREATE OR REPLACE VIEW plagiarism_summary AS
SELECT 
    pc.id as check_id,
    d1.file_name as query_document,
    COUNT(DISTINCT pm.matched_document_id) as unique_matched_documents,
    COUNT(pm.id) as total_matches,
    MAX(pm.similarity_score) as max_similarity,
    AVG(pm.similarity_score) as avg_similarity,
    pc.check_date,
    pc.similarity_threshold
FROM plagiarism_checks pc
JOIN documents d1 ON pc.query_document_id = d1.id
LEFT JOIN plagiarism_matches pm ON pc.id = pm.plagiarism_check_id
GROUP BY pc.id, d1.file_name, pc.check_date, pc.similarity_threshold;
