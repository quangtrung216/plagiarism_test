from __future__ import annotations

import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from .config import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD


class PostgresService:
    """Service for interacting with PostgreSQL database."""
    
    def __init__(self):
        """Initialize PostgreSQL service."""
        self.connection_string = (
            f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
            f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        )
    
    def get_connection(self):
        """Get database connection."""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            conn = psycopg2.connect(self.connection_string)
            return conn
        except ImportError:
            raise ImportError(
                "Missing dependency 'psycopg2-binary'. Install it with: pip install psycopg2-binary"
            )
    
    def create_document_record(
        self,
        file_name: str,
        file_path: str,
        file_size: int,
        file_type: str,
        title: Optional[str] = None,
        author: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[int]:
        """
        Create a new document record in PostgreSQL.
        
        Args:
            file_name: Original file name
            file_path: Stored file path
            file_size: File size in bytes
            file_type: File type (e.g., 'pdf')
            title: Document title
            author: Document author
            metadata: Additional metadata
            
        Returns:
            Document ID or None if failed
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
            INSERT INTO documents (
                file_name, file_path, file_size, file_type, title, author, 
                status, metadata
            ) VALUES (%s, %s, %s, %s, %s, %s, 'pending', %s)
            RETURNING id
            """
            
            metadata_json = json.dumps(metadata) if metadata else None
            
            cursor.execute(query, (
                file_name, file_path, file_size, file_type,
                title, author, metadata_json
            ))
            
            doc_id = cursor.fetchone()[0]
            conn.commit()
            
            return doc_id
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def update_document_status(
        self,
        doc_id: int,
        status: str,
        processed_date: Optional[datetime] = None,
        total_sentences: Optional[int] = None,
        processed_sentences: Optional[int] = None,
        embedding_dimension: Optional[int] = None,
        vector_count: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update document processing status.
        
        Args:
            doc_id: Document ID
            status: New status ('pending', 'processing', 'completed', 'failed')
            processed_date: Processing completion date
            total_sentences: Total sentences found
            processed_sentences: Sentences successfully processed
            embedding_dimension: Embedding vector dimension
            vector_count: Number of vectors stored in Milvus
            error_message: Error message if failed
            
        Returns:
            True if successful, False otherwise
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Build dynamic update query
            update_fields = ["status = %s"]
            params = [status]
            param_index = 2
            
            if processed_date:
                update_fields.append(f"processed_date = %{param_index}")
                params.append(processed_date)
                param_index += 1
            
            if total_sentences is not None:
                update_fields.append(f"total_sentences = %{param_index}")
                params.append(total_sentences)
                param_index += 1
            
            if processed_sentences is not None:
                update_fields.append(f"processed_sentences = %{param_index}")
                params.append(processed_sentences)
                param_index += 1
            
            if embedding_dimension is not None:
                update_fields.append(f"embedding_dimension = %{param_index}")
                params.append(embedding_dimension)
                param_index += 1
            
            if vector_count is not None:
                update_fields.append(f"vector_count = %{param_index}")
                params.append(vector_count)
                param_index += 1
            
            if error_message:
                update_fields.append(f"error_message = %{param_index}")
                params.append(error_message)
                param_index += 1
            
            params.append(doc_id)  # WHERE clause
            
            query = f"""
            UPDATE documents 
            SET {', '.join(update_fields)}
            WHERE id = %{param_index}
            """
            
            cursor.execute(query, tuple(params))
            conn.commit()
            
            return cursor.rowcount > 0
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def save_sentences(
        self,
        doc_id: int,
        sentences_data: List[Dict[str, Any]]
    ) -> int:
        """
        Save processed sentences to database.
        
        Args:
            doc_id: Document ID
            sentences_data: List of sentence data
            
        Returns:
            Number of sentences saved
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
            INSERT INTO sentences (
                document_id, sentence_index, original_sentence, processed_sentence,
                word_count, character_count, page_number, paragraph_number,
                sentence_hash, embedding_vector_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (sentence_hash) DO NOTHING
            """
            
            saved_count = 0
            for sentence_data in sentences_data:
                cursor.execute(query, (
                    doc_id,
                    sentence_data.get('sentence_index'),
                    sentence_data.get('original_sentence'),
                    sentence_data.get('processed_sentence'),
                    sentence_data.get('word_count'),
                    sentence_data.get('character_count'),
                    sentence_data.get('page_number'),
                    sentence_data.get('paragraph_number'),
                    sentence_data.get('sentence_hash'),
                    sentence_data.get('embedding_vector_id')
                ))
                
                if cursor.rowcount > 0:
                    saved_count += 1
            
            conn.commit()
            return saved_count
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def get_document_by_id(self, doc_id: int) -> Optional[Dict[str, Any]]:
        """
        Get document information by ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document data or None
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            query = "SELECT * FROM documents WHERE id = %s"
            cursor.execute(query, (doc_id,))
            
            result = cursor.fetchone()
            
            if result:
                doc_data = dict(result)
                # Parse metadata JSON
                if doc_data.get('metadata'):
                    doc_data['metadata'] = json.loads(doc_data['metadata'])
                return doc_data
            
            return None
            
        except Exception as e:
            raise e
        finally:
            if conn:
                conn.close()
    
    def get_document_sentences(self, doc_id: int) -> List[Dict[str, Any]]:
        """
        Get all sentences for a document.
        
        Args:
            doc_id: Document ID
            
        Returns:
            List of sentence data
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
            SELECT * FROM sentences 
            WHERE document_id = %s 
            ORDER BY sentence_index
            """
            cursor.execute(query, (doc_id,))
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
            
        except Exception as e:
            raise e
        finally:
            if conn:
                conn.close()
    
    def create_plagiarism_check(
        self,
        query_document_id: int,
        similarity_threshold: float = 0.70,
        total_comparisons: int = 0,
        potential_matches: int = 0,
        max_similarity_score: float = 0.0,
        average_similarity_score: float = 0.0,
        processing_time_seconds: int = 0
    ) -> Optional[int]:
        """
        Create plagiarism check record.
        
        Args:
            query_document_id: Document ID being checked
            similarity_threshold: Similarity threshold used
            total_comparisons: Total comparisons made
            potential_matches: Number of potential matches found
            max_similarity_score: Highest similarity score
            average_similarity_score: Average similarity score
            processing_time_seconds: Time taken for processing
            
        Returns:
            Check ID or None if failed
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
            INSERT INTO plagiarism_checks (
                query_document_id, similarity_threshold, total_comparisons,
                potential_matches, max_similarity_score, average_similarity_score,
                processing_time_seconds
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """
            
            cursor.execute(query, (
                query_document_id, similarity_threshold, total_comparisons,
                potential_matches, max_similarity_score, average_similarity_score,
                processing_time_seconds
            ))
            
            check_id = cursor.fetchone()[0]
            conn.commit()
            
            return check_id
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def save_plagiarism_matches(
        self,
        plagiarism_check_id: int,
        matches_data: List[Dict[str, Any]]
    ) -> int:
        """
        Save plagiarism match results.
        
        Args:
            plagiarism_check_id: Check ID
            matches_data: List of match data
            
        Returns:
            Number of matches saved
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
            INSERT INTO plagiarism_matches (
                plagiarism_check_id, query_sentence_id, matched_document_id,
                matched_sentence_id, similarity_score, match_type,
                highlighted_query_sentence, highlighted_matched_sentence,
                context_before_query, context_after_query,
                context_before_matched, context_after_matched
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            for match_data in matches_data:
                cursor.execute(query, (
                    plagiarism_check_id,
                    match_data.get('query_sentence_id'),
                    match_data.get('matched_document_id'),
                    match_data.get('matched_sentence_id'),
                    match_data.get('similarity_score'),
                    match_data.get('match_type', 'exact'),
                    match_data.get('highlighted_query_sentence'),
                    match_data.get('highlighted_matched_sentence'),
                    match_data.get('context_before_query'),
                    match_data.get('context_after_query'),
                    match_data.get('context_before_matched'),
                    match_data.get('context_after_matched')
                ))
            
            conn.commit()
            return len(matches_data)
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def get_document_statistics(self, doc_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed statistics for a document.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Statistics data or None
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            query = "SELECT * FROM document_statistics WHERE id = %s"
            cursor.execute(query, (doc_id,))
            
            result = cursor.fetchone()
            return dict(result) if result else None
            
        except Exception as e:
            raise e
        finally:
            if conn:
                conn.close()
