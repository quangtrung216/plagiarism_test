from typing import List
from nlp.text_preprocess import preprocess_pdf_text, extract_plagiarism_zone, normalize_full_text

class PreprocessService:
    """Service for text preprocessing and analysis"""
    
    @staticmethod
    def preprocess_text(
        text: str,
        language: str = "vi",
        min_words: int = 8,
        max_words: int = 200,
        use_zone: bool = True
    ) -> dict:
        try:
            # Normalize text
            normalized_text = normalize_full_text(text)
            
            # Extract plagiarism zone if enabled
            if use_zone:
                plagiarism_zone = extract_plagiarism_zone(normalized_text)
            else:
                plagiarism_zone = normalized_text
            
            # Preprocess and extract valid sentences
            sentences = preprocess_pdf_text(
                raw_text=plagiarism_zone,
                language=language,
                min_words=min_words,
                max_words=max_words,
                use_zone=False  # Already extracted
            )
            
            return {
                "success": True,
                "total_sentences": len(sentences),
                "sentences": sentences,
                "metadata": {
                    "language": language,
                    "min_words": min_words,
                    "max_words": max_words,
                    "use_zone": use_zone,
                    "original_text_length": len(text),
                    "normalized_text_length": len(normalized_text)
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "sentences": []
            }
    
    @staticmethod
    def analyze_text_structure(text: str) -> dict:
        """
        Analyze text structure to identify key sections
        
        Args:
            text: Raw text to analyze
            
        Returns:
            dict with analysis results
        """
        try:
            normalized_text = normalize_full_text(text)
            plagiarism_zone = extract_plagiarism_zone(normalized_text)
            
            # Calculate statistics
            lines = text.split("\n")
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            
            return {
                "success": True,
                "total_lines": len(lines),
                "total_paragraphs": len(paragraphs),
                "total_characters": len(text),
                "total_words": len(text.split()),
                "plagiarism_zone_length": len(plagiarism_zone),
                "plagiarism_zone_percentage": round((len(plagiarism_zone) / len(text) * 100), 2) if text else 0
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
