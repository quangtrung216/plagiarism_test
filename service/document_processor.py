"""
Document processing pipeline that integrates text processing, embedding services, and metadata management.
"""

import logging
import time
from typing import List, Dict, Any, Optional
from pathlib import Path

from text_process import TextPreprocessor, PDFProcessor
from .embedding_service import EmbeddingService
from ..db.metadata_service import MetadataService
from .highlight_service import HighlightService


class DocumentProcessor:
    """
    Complete document processing pipeline that combines text preprocessing
    and embedding generation for plagiarism detection.
    """
    
    def __init__(
        self,
        min_words: int = 8,
        embedding_model: str = "DEk21_hcmute_embedding",
        log_level: str = "INFO",
        store_metadata: bool = True
    ):
        """
        Initialize the document processor.
        
        Args:
            min_words: Minimum number of words for a sentence to be considered valid
            embedding_model: Name of the embedding model to use
            log_level: Logging level
            store_metadata: Whether to store metadata in PostgreSQL
        """
        # Setup logging
        logging.basicConfig(level=getattr(logging, log_level.upper()))
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.text_preprocessor = TextPreprocessor(min_words=min_words)
        self.pdf_processor = PDFProcessor(min_words=min_words)
        self.embedding_service = EmbeddingService(model_name=embedding_model)
        self.highlight_service = HighlightService()
        
        # Initialize metadata service if enabled
        self.store_metadata = store_metadata
        if self.store_metadata:
            self.metadata_service = MetadataService()
        else:
            self.metadata_service = None
        
        self.logger.info(f"DocumentProcessor initialized with model: {embedding_model}, metadata storage: {store_metadata}")
    
    def process_text_document(self, text: str) -> Dict[str, Any]:
        """
        Process a text document through the complete pipeline.
        
        Args:
            text: Raw text content
            
        Returns:
            Dictionary containing processed results including embeddings
        """
        try:
            self.logger.info("Starting text document processing...")
            
            # Step 1: Text preprocessing
            preprocessed_result = self.text_preprocessor.preprocess_document(text)
            processed_sentences = preprocessed_result['processed_sentences']
            
            self.logger.info(f"Text preprocessing completed. Processed {len(processed_sentences)} sentences")
            
            # Step 2: Generate embeddings
            embedding_result = self.embedding_service.process_document_embeddings(processed_sentences)
            
            # Combine results
            result = {
                'original_text': text,
                'preprocessing_result': preprocessed_result,
                'embedding_result': embedding_result,
                'processing_stats': {
                    'original_text_length': len(text),
                    'original_sentences': len(preprocessed_result['original_sentences']),
                    'processed_sentences': len(processed_sentences),
                    'embedded_sentences': len(embedding_result['embeddings']),
                    'embedding_dimension': embedding_result['stats']['embedding_dimension']
                }
            }
            
            self.logger.info("Text document processing completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing text document: {e}")
            raise
    
    def process_pdf_document(self, pdf_path: str, store_to_db: bool = True) -> Dict[str, Any]:
        """
        Process a PDF document through the complete pipeline.
        
        Args:
            pdf_path: Path to the PDF file
            store_to_db: Whether to store metadata to database
            
        Returns:
            Dictionary containing processed results including embeddings
        """
        try:
            self.logger.info(f"Starting PDF document processing: {pdf_path}")
            
            # Create document record in database if enabled
            doc_id = None
            if self.store_metadata and store_to_db:
                pdf_path_obj = Path(pdf_path)
                doc_id = self.metadata_service.create_document(
                    file_name=pdf_path_obj.name,
                    file_path=str(pdf_path_obj.absolute()),
                    file_type='pdf',
                    file_size=pdf_path_obj.stat().st_size if pdf_path_obj.exists() else None
                )
                self.logger.info(f"Created document record: {doc_id}")
            
            # Step 1: PDF processing (includes text extraction and preprocessing)
            pdf_result = self.pdf_processor.process_pdf(pdf_path)
            
            if 'error' in pdf_result['pdf_info']:
                # Update document with error status
                if self.store_metadata and doc_id:
                    self.metadata_service.update_document_processing(
                        doc_id, 0, 0, 0, 0, 'failed', pdf_result['pdf_info']['error']
                    )
                raise Exception(f"PDF processing error: {pdf_result['pdf_info']['error']}")
            
            processed_sentences = pdf_result['processed_sentences']
            original_sentences = pdf_result['original_sentences']
            
            self.logger.info(f"PDF processing completed. Processed {len(processed_sentences)} sentences")
            
            # Step 2: Generate embeddings
            embedding_result = self.embedding_service.process_document_embeddings(processed_sentences)
            
            # Step 3: Store metadata to database
            if self.store_metadata and doc_id and store_to_db:
                # Update document processing info
                self.metadata_service.update_document_processing(
                    doc_id=doc_id,
                    total_sentences=len(original_sentences),
                    processed_sentences=len(processed_sentences),
                    embedding_dimension=embedding_result['stats']['embedding_dimension'],
                    vector_count=len(embedding_result['embeddings']),
                    status='completed'
                )
                
                # Store sentences with page numbers if available
                page_numbers = None
                if 'sentences_with_metadata' in pdf_result:
                    page_numbers = [s.get('page_number') for s in pdf_result['sentences_with_metadata']]
                
                self.metadata_service.store_sentences(
                    doc_id=doc_id,
                    original_sentences=original_sentences,
                    processed_sentences=processed_sentences,
                    page_numbers=page_numbers
                )
                
                self.logger.info(f"Stored metadata for document {doc_id}")
            
            # Combine results
            result = {
                'pdf_path': pdf_path,
                'pdf_result': pdf_result,
                'embedding_result': embedding_result,
                'document_id': doc_id,
                'processing_stats': {
                    'file_name': pdf_result['pdf_info']['file_name'],
                    'file_size': pdf_result['pdf_info']['file_size'],
                    'original_sentences': pdf_result['stats']['total_sentences'],
                    'processed_sentences': len(processed_sentences),
                    'embedded_sentences': len(embedding_result['embeddings']),
                    'embedding_dimension': embedding_result['stats']['embedding_dimension'],
                    'stored_to_db': store_to_db and self.store_metadata and doc_id is not None
                }
            }
            
            self.logger.info("PDF document processing completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing PDF document: {e}")
            # Update document with error status if we have a doc_id
            if 'doc_id' in locals() and doc_id and self.store_metadata:
                self.metadata_service.update_document_processing(
                    doc_id, 0, 0, 0, 0, 'failed', str(e)
                )
            raise
    
    def process_directory(
        self, 
        directory_path: str, 
        recursive: bool = True,
        file_pattern: str = "*.pdf"
    ) -> List[Dict[str, Any]]:
        """
        Process all PDF documents in a directory.
        
        Args:
            directory_path: Path to the directory containing PDFs
            recursive: Whether to search recursively
            file_pattern: File pattern to match (default: "*.pdf")
            
        Returns:
            List of processing results for each document
        """
        try:
            self.logger.info(f"Starting directory processing: {directory_path}")
            
            directory_path = Path(directory_path)
            
            if not directory_path.exists():
                raise FileNotFoundError(f"Directory not found: {directory_path}")
            
            # Find PDF files
            if recursive:
                pdf_files = list(directory_path.rglob(file_pattern))
            else:
                pdf_files = list(directory_path.glob(file_pattern))
            
            self.logger.info(f"Found {len(pdf_files)} PDF files to process")
            
            results = []
            for pdf_file in pdf_files:
                try:
                    result = self.process_pdf_document(str(pdf_file))
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Error processing {pdf_file}: {e}")
                    results.append({
                        'pdf_path': str(pdf_file),
                        'error': str(e),
                        'processing_stats': {'status': 'failed'}
                    })
            
            successful_results = [r for r in results if 'error' not in r]
            self.logger.info(f"Directory processing completed. Successfully processed {len(successful_results)}/{len(results)} files")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error processing directory: {e}")
            raise
    
    def compare_documents(
        self, 
        doc1_result: Dict[str, Any], 
        doc2_result: Dict[str, Any],
        store_results: bool = True
    ) -> Dict[str, Any]:
        """
        Compare two processed documents for similarity.
        
        Args:
            doc1_result: Processing result of document 1
            doc2_result: Processing result of document 2
            store_results: Whether to store comparison results to database
            
        Returns:
            Dictionary containing comparison results
        """
        try:
            self.logger.info("Starting document comparison...")
            
            # Get embeddings
            embeddings1 = doc1_result['embedding_result']['embeddings']
            embeddings2 = doc2_result['embedding_result']['embeddings']
            
            if len(embeddings1) == 0 or len(embeddings2) == 0:
                return {
                    'error': 'One or both documents have no embeddings',
                    'comparison_stats': {
                        'doc1_sentences': len(embeddings1),
                        'doc2_sentences': len(embeddings2),
                        'status': 'failed'
                    }
                }
            
            # Compare using embedding service
            comparison_result = self.embedding_service.compare_documents(embeddings1, embeddings2)
            
            # Generate highlighted matches if we have document IDs
            highlighted_matches = []
            if (self.store_metadata and 
                doc1_result.get('document_id') and 
                doc2_result.get('document_id')):
                
                # Get sentence data from database
                doc1_sentences = self.metadata_service.get_document_sentences(doc1_result['document_id'])
                doc2_sentences = self.metadata_service.get_document_sentences(doc2_result['document_id'])
                
                # Generate highlights for similar pairs
                for pair in comparison_result['similar_sentence_pairs']:
                    query_idx = pair['doc1_sentence_idx']
                    matched_idx = pair['doc2_sentence_idx']
                    
                    if (query_idx < len(doc1_sentences) and 
                        matched_idx < len(doc2_sentences)):
                        
                        query_sent = doc1_sentences[query_idx]
                        matched_sent = doc2_sentences[matched_idx]
                        
                        # Generate highlighted versions
                        highlighted_query, highlighted_matched = self.highlight_service.highlight_sentence_segments(
                            query_sent['original_sentence'],
                            matched_sent['original_sentence'],
                            pair['similarity']
                        )
                        
                        # Get context
                        doc1_context = self.highlight_service.get_sentence_context(
                            [s['original_sentence'] for s in doc1_sentences], query_idx
                        )
                        doc2_context = self.highlight_service.get_sentence_context(
                            [s['original_sentence'] for s in doc2_sentences], matched_idx
                        )
                        
                        highlighted_match = {
                            'query_sentence_id': query_sent['id'],
                            'matched_sentence_id': matched_sent['id'],
                            'similarity_score': pair['similarity'],
                            'highlighted_query_sentence': highlighted_query,
                            'highlighted_matched_sentence': highlighted_matched,
                            'context_before_query': " ".join(doc1_context['before']),
                            'context_after_query': " ".join(doc1_context['after']),
                            'context_before_matched': " ".join(doc2_context['before']),
                            'context_after_matched': " ".join(doc2_context['after'])
                        }
                        highlighted_matches.append(highlighted_match)
            
            # Store plagiarism check if enabled
            check_id = None
            if (self.store_metadata and store_results and 
                doc1_result.get('document_id')):
                
                check_id = self.metadata_service.create_plagiarism_check(
                    query_document_id=doc1_result['document_id'],
                    similarity_threshold=0.7,
                    total_comparisons=len(embeddings1) * len(embeddings2),
                    potential_matches=len(comparison_result['similar_sentence_pairs']),
                    max_similarity=comparison_result['max_similarity'],
                    average_similarity=comparison_result['average_similarity']
                )
                
                # Store matches with highlights
                if highlighted_matches:
                    match_data = []
                    for i, pair in enumerate(comparison_result['similar_sentence_pairs']):
                        if i < len(highlighted_matches):
                            match_data.append({
                                'query_sentence_id': highlighted_matches[i]['query_sentence_id'],
                                'matched_document_id': doc2_result['document_id'],
                                'matched_sentence_id': highlighted_matches[i]['matched_sentence_id'],
                                'similarity_score': pair['similarity'],
                                'match_type': 'exact' if pair['similarity'] >= 0.9 else 'paraphrase',
                                'highlighted_query_sentence': highlighted_matches[i]['highlighted_query_sentence'],
                                'highlighted_matched_sentence': highlighted_matches[i]['highlighted_matched_sentence'],
                                'context_before_query': highlighted_matches[i]['context_before_query'],
                                'context_after_query': highlighted_matches[i]['context_after_query'],
                                'context_before_matched': highlighted_matches[i]['context_before_matched'],
                                'context_after_matched': highlighted_matches[i]['context_after_matched']
                            })
                    
                    self.metadata_service.store_plagiarism_matches(check_id, match_data)
                    self.logger.info(f"Stored plagiarism check {check_id} with {len(match_data)} matches")
            
            # Add document metadata
            result = {
                'doc1_info': doc1_result.get('processing_stats', {}),
                'doc2_info': doc2_result.get('processing_stats', {}),
                'comparison_result': comparison_result,
                'highlighted_matches': highlighted_matches,
                'plagiarism_check_id': check_id,
                'comparison_stats': {
                    'doc1_sentences': len(embeddings1),
                    'doc2_sentences': len(embeddings2),
                    'max_similarity': comparison_result['max_similarity'],
                    'average_similarity': comparison_result['average_similarity'],
                    'similar_pairs_found': len(comparison_result['similar_sentence_pairs']),
                    'highlighted_matches': len(highlighted_matches),
                    'status': 'completed',
                    'stored_to_db': store_results and self.store_metadata and check_id is not None
                }
            }
            
            self.logger.info("Document comparison completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error comparing documents: {e}")
            raise
    
    def find_similar_documents(
        self, 
        query_doc_result: Dict[str, Any], 
        corpus_results: List[Dict[str, Any]],
        similarity_threshold: float = 0.7,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find documents similar to a query document from a corpus.
        
        Args:
            query_doc_result: Processing result of the query document
            corpus_results: List of processing results for corpus documents
            similarity_threshold: Minimum similarity threshold
            top_k: Maximum number of results to return
            
        Returns:
            List of similar documents with similarity scores
        """
        try:
            self.logger.info("Finding similar documents...")
            
            query_embeddings = query_doc_result['embedding_result']['embeddings']
            
            if len(query_embeddings) == 0:
                return []
            
            similar_docs = []
            
            for i, corpus_doc in enumerate(corpus_results):
                try:
                    corpus_embeddings = corpus_doc['embedding_result']['embeddings']
                    
                    if len(corpus_embeddings) == 0:
                        continue
                    
                    # Compare documents
                    comparison = self.compare_documents(query_doc_result, corpus_doc)
                    max_sim = comparison['comparison_result']['max_similarity']
                    
                    if max_sim >= similarity_threshold:
                        similar_docs.append({
                            'corpus_index': i,
                            'max_similarity': max_sim,
                            'average_similarity': comparison['comparison_result']['average_similarity'],
                            'similar_pairs': len(comparison['comparison_result']['similar_sentence_pairs']),
                            'document_info': corpus_doc.get('processing_stats', {}),
                            'comparison_details': comparison
                        })
                        
                except Exception as e:
                    self.logger.error(f"Error comparing with document {i}: {e}")
                    continue
            
            # Sort by max similarity
            similar_docs.sort(key=lambda x: x['max_similarity'], reverse=True)
            
            # Return top_k results
            results = similar_docs[:top_k]
            
            self.logger.info(f"Found {len(results)} similar documents above threshold {similarity_threshold}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error finding similar documents: {e}")
            raise
