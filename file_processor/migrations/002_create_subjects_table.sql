-- Create subjects table
CREATE TABLE IF NOT EXISTS subjects (
    subject_id VARCHAR(50) PRIMARY KEY,
    subject_name VARCHAR(200) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_subjects_name ON subjects(subject_name);

-- Insert sample subjects (optional)
INSERT INTO subjects (subject_id, subject_name, description) VALUES
('toan', 'Toán', 'Các môn học liên quan đến toán học'),
('lap_trinh', 'Lập trình', 'Các môn học lập trình và khoa học máy tính'),
('tieng_anh', 'Tiếng Anh', 'Các môn học tiếng Anh'),
('vat_ly', 'Vật lý', 'Các môn học vật lý'),
('hoa_hoc', 'Hóa học', 'Các môn học hóa học')
ON CONFLICT (subject_id) DO NOTHING;
