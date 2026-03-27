"""
Database service for managing document metadata and plagiarism detection results.
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from .postgres import get_session_maker


class MetadataService:
    """
    Service for managing document metadata in PostgreSQL database.
    """
    
    def __init__(self):
        """Initialize the metadata service."""
        self.session_maker = get_session_maker()
        self.logger = logging.getLogger(__name__)
    
    def _get_sentence_hash(self, sentence: str) -> str:
        """Generate a unique hash for a sentence."""
        return hashlib.sha256(sentence.encode('utf-8')).hexdigest()
    
    def create_document(
        self, 
        file_name: str, 
        file_path: str, 
        file_type: str,
        file_size: Optional[int] = None,
        title: Optional[str] = None,
        author: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Create a new document record.
        
        Args:
            file_name: Name of the file
            file_path: Full path to the file
            file_type: Type of file (pdf, txt, docx, etc.)
            file_size: Size of file in bytes
            title: Document title
            author: Document author
            metadata: Additional metadata as JSON
            
        Returns:
            Document ID
        """
        try:
            with self.session_maker() as session:
                # Create document record
                doc_data = {
                    'file_name': file_name,
                    'file_path': file_path,
                    'file_type': file_type,
                    'file_size': file_size,
                    'title': title,
                    'author': author,
                    'metadata': json.dumps(metadata) if metadata else None,
                    'status': 'pending'
                }
                
                # Use raw SQL for better control
                query = """
                INSERT INTO documents (file_name, file_path, file_type, file_size, title, author, metadata, status)
                VALUES (%(file_name)s, %(file_path)s, %(file_type)s, %(file_size)s, %(title)s, %(author)s, %(metadata)s, %(status)s)
                RETURNING id
                """
                
                result = session.execute(query, doc_data)
                doc_id = result.scalar()
                session.commit()
                
                self.logger.info(f"Created document record: {doc_id}")
                return doc_id
                
        except Exception as e:
            self.logger.error(f"Error creating document: {e}")
            session.rollback()
            raise
    
    def update_document_processing(
        self, 
        doc_id: int, 
        total_sentences: int,
        processed_sentences: int,
        embedding_dimension: int,
        vector_count: int = 0,
        status: str = 'completed',
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update document processing information.
        
        Args:
            doc_id: Document ID
            total_sentences: Total number of sentences in document
            processed_sentences: Number of processed sentences
            embedding_dimension: Dimension of embedding vectors
            vector_count: Number of vectors stored in vector DB
            status: Processing status
            error_message: Error message if processing failed
            
        Returns:
            True if successful
        """
        try:
            with self.session_maker() as session:
                query = """
                UPDATE documents 
                SET total_sentences = %s,
                    processed_sentences = %s,
                    embedding_dimension = %s,
                    vector_count = %s,
                    processed_date = CURRENT_TIMESTAMP,
                    status = %s,
                    error_message = %s
                WHERE id = %s
                """
                
                session.execute(query, (
                    total_sentences, processed_sentences, embedding_dimension, 
                    vector_count, status, error_message, doc_id
                ))
                session.commit()
                
                self.logger.info(f"Updated document {doc_id} processing info")
                return True
                
        except Exception as e:
            self.logger.error(f"Error updating document processing: {e}")
            session.rollback()
            return False
    
    def store_sentences(
        self, 
        doc_id: int, 
        original_sentences: List[str],
        processed_sentences: List[str],
        embedding_vector_ids: Optional[List[str]] = None,
        page_numbers: Optional[List[int]] = None
    ) -> bool:
        """
        Store sentences for a document.
        
        Args:
            doc_id: Document ID
            original_sentences: List of original sentences
            processed_sentences: List of processed sentences
            embedding_vector_ids: List of vector IDs from Milvus
            page_numbers: List of page numbers (for PDFs)
            
        Returns:
            True if successful
        """
        try:
            with self.session_maker() as session:
                # Prepare sentence data
                sentence_data = []
                for i, (orig_sent, proc_sent) in enumerate(zip(original_sentences, processed_sentences)):
                    vector_id = embedding_vector_ids[i] if embedding_vector_ids and i < len(embedding_vector_ids) else None
                    page_num = page_numbers[i] if page_numbers and i < len(page_numbers) else None
                    sentence_hash = self._get_sentence_hash(proc_sent)
                    
                    sentence_data.append({
                        'document_id': doc_id,
                        'sentence_index': i,
                        'original_sentence': orig_sent,
                        'processed_sentence': proc_sent,
                        'word_count': len(proc_sent.split()),
                        'character_count': len(proc_sent),
                        'page_number': page_num,
                        'sentence_hash': sentence_hash,
                        'embedding_vector_id': vector_id
                    })
                
                # Insert sentences using executemany for better performance
                query = """
                INSERT INTO sentences (
                    document_id, sentence_index, original_sentence, processed_sentence,
                    word_count, character_count, page_number, sentence_hash, embedding_vector_id
                ) VALUES (
                    %(document_id)s, %(sentence_index)s, %(original_sentence)s, %(processed_sentence)s,
                    %(word_count)s, %(character_count)s, %(page_number)s, %(sentence_hash)s, %(embedding_vector_id)s
                )
                ON CONFLICT (sentence_hash) DO NOTHING
                """
                
                session.execute(query, sentence_data)
                session.commit()
                
                self.logger.info(f"Stored {len(sentence_data)} sentences for document {doc_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error storing sentences: {e}")
            session.rollback()
            return False
    
    def get_document_by_id(self, doc_id: int) -> Optional[Dict[str, Any]]:
        """Get document information by ID."""
        try:
            with self.session_maker() as session:
                query = """
                SELECT id, file_name, file_path, file_type, file_size, title, author,
                       upload_date, processed_date, total_sentences, processed_sentences,
                       embedding_dimension, vector_count, status, error_message, metadata
                FROM documents WHERE id = %s
                """
                
                result = session.execute(query, (doc_id,))
                row = result.fetchone()
                
                if row:
                    return {
                        'id': row[0], 'file_name': row[1], 'file_path': row[2],
                        'file_type': row[3], 'file_size': row[4], 'title': row[5],
                        'author': row[6], 'upload_date': row[7], 'processed_date': row[8],
                        'total_sentences': row[9], 'processed_sentences': row[10],
                        'embedding_dimension': row[11], 'vector_count': row[12],
                        'status': row[13], 'error_message': row[14], 'metadata': row[15]
                    }
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting document {doc_id}: {e}")
            return None
    
    def get_document_sentences(self, doc_id: int) -> List[Dict[str, Any]]:
        """Get all sentences for a document."""
        try:
            with self.session_maker() as session:
                query = """
                SELECT id, sentence_index, original_sentence, processed_sentence,
                       word_count, character_count, page_number, embedding_vector_id
                FROM sentences 
                WHERE document_id = %s 
                ORDER BY sentence_index
                """
                
                result = session.execute(query, (doc_id,))
                rows = result.fetchall()
                
                sentences = []
                for row in rows:
                    sentences.append({
                        'id': row[0], 'sentence_index': row[1],
                        'original_sentence': row[2], 'processed_sentence': row[3],
                        'word_count': row[4], 'character_count': row[5],
                        'page_number': row[6], 'embedding_vector_id': row[7]
                    })
                
                return sentences
                
        except Exception as e:
            self.logger.error(f"Error getting sentences for document {doc_id}: {e}")
            return []
    
    def create_plagiarism_check(
        self, 
        query_document_id: int,
        similarity_threshold: float = 0.70,
        total_comparisons: int = 0,
        potential_matches: int = 0,
        max_similarity: float = 0.0,
        average_similarity: float = 0.0,
        processing_time: int = 0
    ) -> int:
        """Create a plagiarism check record."""
        try:
            with self.session_maker() as session:
                query = """
                INSERT INTO plagiarism_checks (
                    query_document_id, similarity_threshold, total_comparisons,
                    potential_matches, max_similarity_score, average_similarity_score,
                    processing_time_seconds
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """
                
                result = session.execute(query, (
                    query_document_id, similarity_threshold, total_comparisons,
                    potential_matches, max_similarity, average_similarity, processing_time
                ))
                check_id = result.scalar()
                session.commit()
                
                self.logger.info(f"Created plagiarism check: {check_id}")
                return check_id
                
        except Exception as e:
            self.logger.error(f"Error creating plagiarism check: {e}")
            session.rollback()
            raise
    
    def store_plagiarism_matches(
        self, 
        plagiarism_check_id: int,
        matches: List[Dict[str, Any]]
    ) -> bool:
        """Store plagiarism match results."""
        try:
            with self.session_maker() as session:
                match_data = []
                for match in matches:
                    match_data.append({
                        'plagiarism_check_id': plagiarism_check_id,
                        'query_sentence_id': match['query_sentence_id'],
                        'matched_document_id': match['matched_document_id'],
                        'matched_sentence_id': match['matched_sentence_id'],
                        'similarity_score': match['similarity_score'],
                        'match_type': match.get('match_type', 'exact'),
                        'highlighted_query_sentence': match.get('highlighted_query_sentence'),
                        'highlighted_matched_sentence': match.get('highlighted_matched_sentence'),
                        'context_before_query': match.get('context_before_query'),
                        'context_after_query': match.get('context_after_query'),
                        'context_before_matched': match.get('context_before_matched'),
                        'context_after_matched': match.get('context_after_matched')
                    })
                
                if match_data:
                    query = """
                    INSERT INTO plagiarism_matches (
                        plagiarism_check_id, query_sentence_id, matched_document_id,
                        matched_sentence_id, similarity_score, match_type,
                        highlighted_query_sentence, highlighted_matched_sentence,
                        context_before_query, context_after_query,
                        context_before_matched, context_after_matched
                    ) VALUES (
                        %(plagiarism_check_id)s, %(query_sentence_id)s, %(matched_document_id)s,
                        %(matched_sentence_id)s, %(similarity_score)s, %(match_type)s,
                        %(highlighted_query_sentence)s, %(highlighted_matched_sentence)s,
                        %(context_before_query)s, %(context_after_query)s,
                        %(context_before_matched)s, %(context_after_matched)s
                    )
                    """
                    
                    session.execute(query, match_data)
                    session.commit()
                    
                    self.logger.info(f"Stored {len(match_data)} plagiarism matches")
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error storing plagiarism matches: {e}")
            session.rollback()
            return False
    
    def get_plagiarism_results(self, check_id: int) -> Dict[str, Any]:
        """Get plagiarism check results with matches."""
        try:
            with self.session_maker() as session:
                # Get check info
                check_query = """
                SELECT pc.*, d.file_name as query_document_name
                FROM plagiarism_checks pc
                JOIN documents d ON pc.query_document_id = d.id
                WHERE pc.id = %s
                """
                
                check_result = session.execute(check_query, (check_id,))
                check_row = check_result.fetchone()
                
                if not check_row:
                    return None
                
                # Get matches
                matches_query = """
                SELECT pm.*, 
                       d.file_name as matched_document_name,
                       qs.original_sentence as query_original,
                       qs.processed_sentence as query_processed,
                       ms.original_sentence as matched_original,
                       ms.processed_sentence as matched_processed
                FROM plagiarism_matches pm
                JOIN documents d ON pm.matched_document_id = d.id
                JOIN sentences qs ON pm.query_sentence_id = qs.id
                JOIN sentences ms ON pm.matched_sentence_id = ms.id
                WHERE pm.plagiarism_check_id = %s
                ORDER BY pm.similarity_score DESC
                """
                
                matches_result = session.execute(matches_query, (check_id,))
                matches_rows = matches_result.fetchall()
                
                matches = []
                for row in matches_rows:
                    matches.append({
                        'id': row[0], 'query_sentence_id': row[1],
                        'matched_document_id': row[2], 'matched_sentence_id': row[3],
                        'similarity_score': float(row[4]), 'match_type': row[5],
                        'highlighted_query_sentence': row[6],
                        'highlighted_matched_sentence': row[7],
                        'context_before_query': row[8], 'context_after_query': row[9],
                        'context_before_matched': row[10], 'context_after_matched': row[11],
                        'matched_document_name': row[12],
                        'query_original': row[13], 'query_processed': row[14],
                        'matched_original': row[15], 'matched_processed': row[16]
                    })
                
                return {
                    'check_id': check_id,
                    'query_document_id': check_row[1],
                    'query_document_name': check_row[14],
                    'check_date': check_row[2],
                    'similarity_threshold': float(check_row[3]),
                    'total_comparisons': check_row[4],
                    'potential_matches': check_row[5],
                    'max_similarity_score': float(check_row[6]),
                    'average_similarity_score': float(check_row[7]),
                    'status': check_row[8],
                    'processing_time_seconds': check_row[9],
                    'matches': matches
                }
                
        except Exception as e:
            self.logger.error(f"Error getting plagiarism results {check_id}: {e}")
            return None
    
    def get_document_statistics(self) -> List[Dict[str, Any]]:
        """Get document statistics."""
        try:
            with self.session_maker() as session:
                query = """
                SELECT * FROM document_statistics
                ORDER BY upload_date DESC
                """
                
                result = session.execute(query)
                rows = result.fetchall()
                
                stats = []
                for row in rows:
                    stats.append({
                        'id': row[0], 'file_name': row[1], 'total_sentences': row[2],
                        'processed_sentences': row[3], 'vector_count': row[4],
                        'status': row[5], 'upload_date': row[6], 'processed_date': row[7],
                        'stored_sentences': row[8], 'avg_sentence_length': float(row[9]) if row[9] else 0,
                        'max_sentence_length': row[10]
                    })
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Error getting document statistics: {e}")
            return []
    
    def search_documents(self, file_name_pattern: str = None, status: str = None) -> List[Dict[str, Any]]:
        """Search documents by filename pattern or status."""
        try:
            with self.session_maker() as session:
                conditions = []
                params = []
                
                if file_name_pattern:
                    conditions.append("file_name ILIKE %s")
                    params.append(f"%{file_name_pattern}%")
                
                if status:
                    conditions.append("status = %s")
                    params.append(status)
                
                where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
                
                query = f"""
                SELECT id, file_name, file_type, file_size, title, author,
                       upload_date, processed_date, total_sentences, processed_sentences,
                       status, error_message
                FROM documents{where_clause}
                ORDER BY upload_date DESC
                """
                
                result = session.execute(query, params)
                rows = result.fetchall()
                
                documents = []
                for row in rows:
                    documents.append({
                        'id': row[0], 'file_name': row[1], 'file_type': row[2],
                        'file_size': row[3], 'title': row[4], 'author': row[5],
                        'upload_date': row[6], 'processed_date': row[7],
                        'total_sentences': row[8], 'processed_sentences': row[9],
                        'status': row[10], 'error_message': row[11]
                    })
                
                return documents
                
        except Exception as e:
            self.logger.error(f"Error searching documents: {e}")
            return []
