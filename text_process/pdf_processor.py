from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional, Union

try:
    import PyPDF2
except ImportError:
    raise ImportError(
        "Missing dependency 'PyPDF2'. Install it with: pip install PyPDF2"
    )

from .preprocessor import TextPreprocessor


class PDFProcessor:
    """PDF processing utilities for extracting and preprocessing text from PDF files."""
    
    def __init__(self, min_words: int = 8):
        """
        Initialize PDF processor.
        
        Args:
            min_words: Minimum number of words for a sentence to be considered valid
        """
        self.preprocessor = TextPreprocessor(min_words=min_words)
    
    def extract_text_from_pdf(self, pdf_path: Union[str, Path]) -> str:
        """
        Extract text from PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text as string
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if not pdf_path.suffix.lower() == '.pdf':
            raise ValueError(f"File is not a PDF: {pdf_path}")
        
        text = ""
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    text += page_text + "\n"
                    
        except Exception as e:
            raise RuntimeError(f"Error reading PDF file {pdf_path}: {e}")
        
        return text
    
    def process_pdf(self, pdf_path: Union[str, Path]) -> dict:
        """
        Process PDF file: extract text and preprocess it.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with processing results
        """
        # Extract text from PDF
        raw_text = self.extract_text_from_pdf(pdf_path)
        
        # Preprocess the text
        result = self.preprocessor.preprocess_document(raw_text)
        
        # Add PDF metadata
        result['pdf_info'] = {
            'file_path': str(pdf_path),
            'file_name': Path(pdf_path).name,
            'file_size': os.path.getsize(pdf_path)
        }
        
        return result
    
    def process_pdf_to_sentences(self, pdf_path: Union[str, Path]) -> List[str]:
        """
        Process PDF file and return only the processed sentences.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of processed sentences
        """
        result = self.process_pdf(pdf_path)
        return result['processed_sentences']
    
    def process_multiple_pdfs(self, pdf_paths: List[Union[str, Path]]) -> List[dict]:
        """
        Process multiple PDF files.
        
        Args:
            pdf_paths: List of paths to PDF files
            
        Returns:
            List of processing results for each PDF
        """
        results = []
        
        for pdf_path in pdf_paths:
            try:
                result = self.process_pdf(pdf_path)
                results.append(result)
            except Exception as e:
                # Add error result for failed processing
                error_result = {
                    'pdf_info': {
                        'file_path': str(pdf_path),
                        'file_name': Path(pdf_path).name,
                        'error': str(e)
                    },
                    'original_sentences': [],
                    'processed_sentences': [],
                    'stats': {
                        'total_sentences': 0,
                        'valid_sentences': 0,
                        'filtered_sentences': 0,
                        'final_sentences': 0
                    }
                }
                results.append(error_result)
        
        return results
    
    def process_directory(self, directory_path: Union[str, Path], recursive: bool = True) -> List[dict]:
        """
        Process all PDF files in a directory.
        
        Args:
            directory_path: Path to directory containing PDF files
            recursive: Whether to search recursively in subdirectories
            
        Returns:
            List of processing results for each PDF
        """
        directory_path = Path(directory_path)
        
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        if not directory_path.is_dir():
            raise ValueError(f"Path is not a directory: {directory_path}")
        
        # Find all PDF files
        if recursive:
            pdf_files = list(directory_path.rglob("*.pdf"))
        else:
            pdf_files = list(directory_path.glob("*.pdf"))
        
        if not pdf_files:
            print(f"No PDF files found in {directory_path}")
            return []
        
        print(f"Found {len(pdf_files)} PDF files")
        
        return self.process_multiple_pdfs(pdf_files)
    
    def extract_sentences_with_metadata(self, pdf_path: Union[str, Path]) -> List[dict]:
        """
        Extract sentences with metadata for each sentence.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of dictionaries with sentence and metadata
        """
        result = self.process_pdf(pdf_path)
        
        sentences_with_metadata = []
        
        for i, sentence in enumerate(result['processed_sentences']):
            sentence_info = {
                'sentence_id': i,
                'sentence': sentence,
                'source_file': result['pdf_info']['file_name'],
                'file_path': result['pdf_info']['file_path'],
                'word_count': len(sentence.split()),
                'character_count': len(sentence)
            }
            sentences_with_metadata.append(sentence_info)
        
        return sentences_with_metadata
