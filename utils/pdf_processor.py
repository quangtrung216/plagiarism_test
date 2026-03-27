from __future__ import annotations

import os
import hashlib
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    import PyPDF2
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    raise ImportError(
        "Missing dependency 'PyPDF2'. Install it with: pip install PyPDF2>=3.0.0"
    )


class PDFProcessor:
    """Processor for extracting text and metadata from PDF files."""
    
    def __init__(self):
        """Initialize PDF processor."""
        pass
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract text and metadata from PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with extracted text and metadata
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                
                # Extract basic metadata
                metadata = self._extract_pdf_metadata(pdf_reader)
                
                # Extract text from all pages
                pages_text = []
                full_text = ""
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():
                            pages_text.append({
                                'page_number': page_num,
                                'text': page_text.strip(),
                                'character_count': len(page_text)
                            })
                            full_text += page_text + "\n"
                    except Exception as e:
                        # Skip pages that can't be processed
                        pages_text.append({
                            'page_number': page_num,
                            'text': "",
                            'character_count': 0,
                            'error': str(e)
                        })
                
                return {
                    'success': True,
                    'full_text': full_text.strip(),
                    'pages': pages_text,
                    'total_pages': len(pdf_reader.pages),
                    'metadata': metadata,
                    'file_info': self._get_file_info(pdf_path)
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'full_text': '',
                'pages': [],
                'total_pages': 0,
                'metadata': {},
                'file_info': {}
            }
    
    def _extract_pdf_metadata(self, pdf_reader: PdfReader) -> Dict[str, Any]:
        """Extract metadata from PDF reader."""
        metadata = {}
        
        if pdf_reader.metadata:
            metadata = {
                'title': pdf_reader.metadata.get('/Title', '').strip(),
                'author': pdf_reader.metadata.get('/Author', '').strip(),
                'subject': pdf_reader.metadata.get('/Subject', '').strip(),
                'creator': pdf_reader.metadata.get('/Creator', '').strip(),
                'producer': pdf_reader.metadata.get('/Producer', '').strip(),
                'creation_date': str(pdf_reader.metadata.get('/CreationDate', '')),
                'modification_date': str(pdf_reader.metadata.get('/ModDate', ''))
            }
        
        return metadata
    
    def _get_file_info(self, pdf_path: str) -> Dict[str, Any]:
        """Get basic file information."""
        try:
            stat = os.stat(pdf_path)
            file_hash = self._calculate_file_hash(pdf_path)
            
            return {
                'file_name': os.path.basename(pdf_path),
                'file_path': pdf_path,
                'file_size': stat.st_size,
                'file_hash': file_hash,
                'created_time': stat.st_ctime,
                'modified_time': stat.st_mtime
            }
        except Exception:
            return {}
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file."""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return ""
    
    def extract_text_with_page_numbers(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extract text with page number information for sentence processing.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of dictionaries with text and page info
        """
        result = self.extract_text_from_pdf(pdf_path)
        
        if not result['success']:
            return []
        
        page_texts = []
        for page in result['pages']:
            if page.get('text', '').strip():
                page_texts.append({
                    'page_number': page['page_number'],
                    'text': page['text'],
                    'character_count': page['character_count']
                })
        
        return page_texts
    
    def validate_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Validate PDF file and check if it can be processed.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Validation result
        """
        if not os.path.exists(pdf_path):
            return {
                'valid': False,
                'error': 'File not found'
            }
        
        if not pdf_path.lower().endswith('.pdf'):
            return {
                'valid': False,
                'error': 'File is not a PDF'
            }
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                
                # Check if PDF has pages
                if len(pdf_reader.pages) == 0:
                    return {
                        'valid': False,
                        'error': 'PDF has no pages'
                    }
                
                # Try to extract text from first page
                first_page = pdf_reader.pages[0]
                sample_text = first_page.extract_text()
                
                return {
                    'valid': True,
                    'total_pages': len(pdf_reader.pages),
                    'has_text': len(sample_text.strip()) > 0,
                    'sample_text_length': len(sample_text.strip()),
                    'file_size': os.path.getsize(pdf_path)
                }
                
        except Exception as e:
            return {
                'valid': False,
                'error': f'PDF validation failed: {str(e)}'
            }
