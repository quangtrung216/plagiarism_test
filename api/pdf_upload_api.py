from __future__ import annotations

import os
import tempfile
import hashlib
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

from utils.pdf_processor import PDFProcessor
from text_process.minhash_processor import MinHashProcessor
from text_process.preprocessor import TextPreprocessor
from service.document_service import DocumentService
from db.postgres_service import PostgresService


# Pydantic models for API responses
class UploadResponse(BaseModel):
    success: bool
    message: str
    document_id: Optional[int] = None
    file_info: Optional[Dict[str, Any]] = None
    processing_stats: Optional[Dict[str, Any]] = None


class DocumentStatus(BaseModel):
    document_id: int
    status: str
    total_sentences: int
    processed_sentences: int
    vector_count: int
    error_message: Optional[str] = None


# Initialize FastAPI app
app = FastAPI(
    title="PDF Upload API with MinHash",
    description="Upload PDF documents with automatic MinHash generation and embedding processing",
    version="1.0.0"
)

# Initialize services
pdf_processor = PDFProcessor()
minhash_processor = MinHashProcessor(num_perm=128, threshold=0.8)
text_preprocessor = TextPreprocessor()
doc_service = DocumentService()
postgres_service = PostgresService()


def calculate_sentence_hash(sentence: str) -> str:
    """Calculate hash for sentence deduplication."""
    return hashlib.sha256(sentence.encode('utf-8')).hexdigest()


def process_pdf_document(
    file_path: str,
    file_name: str,
    file_size: int,
    doc_id: int,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process uploaded PDF document through the complete pipeline.
    
    Args:
        file_path: Path to uploaded PDF file
        file_name: Original file name
        file_size: File size in bytes
        doc_id: Document ID from database
        metadata: Additional metadata
        
    Returns:
        Processing result dictionary
    """
    try:
        # Update status to processing
        postgres_service.update_document_status(doc_id, 'processing')
        
        # Step 1: Extract text from PDF
        pdf_result = pdf_processor.extract_text_from_pdf(file_path)
        
        if not pdf_result['success']:
            postgres_service.update_document_status(
                doc_id, 'failed', 
                error_message=f"PDF extraction failed: {pdf_result.get('error', 'Unknown error')}"
            )
            return {
                'success': False,
                'error': f"PDF extraction failed: {pdf_result.get('error', 'Unknown error')}"
            }
        
        full_text = pdf_result['full_text']
        pdf_metadata = pdf_result['metadata']
        
        # Combine PDF metadata with provided metadata
        combined_metadata = {
            'pdf_info': pdf_metadata,
            'file_info': pdf_result['file_info']
        }
        
        # Only add metadata if provided and not empty
        if parsed_metadata:  # parsed_metadata đã được xử lý ở trên
            combined_metadata.update(parsed_metadata)
        
        # Step 2: Preprocess text and extract sentences
        preprocess_result = text_preprocessor.preprocess_document(full_text)
        processed_sentences = preprocess_result['processed_sentences']
        original_sentences = preprocess_result['original_sentences']
        
        if not processed_sentences:
            postgres_service.update_document_status(
                doc_id, 'failed',
                error_message="No valid sentences found after preprocessing"
            )
            return {
                'success': False,
                'error': "No valid sentences found after preprocessing"
            }
        
        # Step 3: Generate MinHash signature for the entire document
        doc_minhash_signature = minhash_processor.get_minhash_signature_from_sentences(
            processed_sentences
        )
        
        # Step 4: Generate embeddings and upload to Milvus
        try:
            upload_result = doc_service.upload_document(
                text=full_text,
                subject_id=1,  # Default subject ID, can be made configurable
                doc_id=doc_id,
                metadata={
                    **combined_metadata,
                    'minhash_signature': doc_minhash_signature,
                    'processing_method': 'pdf_upload_api'
                }
            )
            
            # Update document status to completed
            postgres_service.update_document_status(
                doc_id, 'completed',
                total_sentences=len(original_sentences),
                processed_sentences=len(processed_sentences),
                vector_count=1  # Document-level vector
            )
            
        except Exception as e:
            # Update document status to failed
            postgres_service.update_document_status(
                doc_id, 'failed',
                error_message=f"Milvus upload failed: {str(e)}"
            )
            return {
                'success': False,
                'error': f"Milvus upload failed: {str(e)}"
            }
        
        # Step 5: Prepare sentence data for PostgreSQL
        sentences_data = []
        page_texts = pdf_processor.extract_text_with_page_numbers(file_path)
        
        # Create a mapping of page numbers to text
        page_text_mapping = {}
        for page_info in page_texts:
            page_text_mapping[page_info['page_number']] = page_info['text']
        
        # Map processed sentences back to original sentences and pages
        sentence_index = 0
        for i, original_sentence in enumerate(original_sentences):
            if i < len(processed_sentences) and processed_sentences[i].strip():
                processed_sentence = processed_sentences[i]
                
                # Find which page this sentence belongs to
                page_number = None
                for page_num, page_text in page_text_mapping.items():
                    if original_sentence in page_text:
                        page_number = page_num
                        break
                
                # Calculate word count and character count
                words = processed_sentence.split()
                word_count = len(words)
                character_count = len(processed_sentence)
                
                # Generate sentence hash
                sentence_hash = calculate_sentence_hash(processed_sentence)
                
                sentences_data.append({
                    'sentence_index': sentence_index,
                    'original_sentence': original_sentence,
                    'processed_sentence': processed_sentence,
                    'word_count': word_count,
                    'character_count': character_count,
                    'page_number': page_number,
                    'paragraph_number': None,  # Can be enhanced later
                    'sentence_hash': sentence_hash,
                    'embedding_vector_id': f"doc_{doc_id}_sent_{sentence_index}"
                })
                
                sentence_index += 1
        
        # Step 6: Save sentences to PostgreSQL
        saved_sentences_count = postgres_service.save_sentences(doc_id, sentences_data)
        
        # Step 7: Update document status to completed
        postgres_service.update_document_status(
            doc_id=doc_id,
            status='completed',
            processed_date=datetime.now(),
            total_sentences=len(original_sentences),
            processed_sentences=len(processed_sentences),
            embedding_dimension=len(upload_result['processed_doc']['document_embedding']),
            vector_count=1,  # Document-level vector
            error_message=None
        )
        
        return {
            'success': True,
            'document_id': doc_id,
            'processing_stats': {
                'total_sentences': len(original_sentences),
                'processed_sentences': len(processed_sentences),
                'saved_sentences': saved_sentences_count,
                'minhash_signature': doc_minhash_signature,
                'embedding_dimension': len(upload_result['processed_doc']['document_embedding']),
                'pdf_pages': pdf_result['total_pages'],
                'file_size': file_size
            },
            'upload_result': {
                'collection_name': upload_result['collection_name'],
                'milvus_insert_id': upload_result['insert_result'].primary_keys[0] if upload_result['insert_result'].primary_keys else None
            }
        }
        
    except Exception as e:
        # Update status to failed
        postgres_service.update_document_status(
            doc_id, 'failed',
            error_message=str(e)
        )
        
        return {
            'success': False,
            'error': str(e),
            'document_id': doc_id
        }


@app.post("/upload-pdf", response_model=UploadResponse)
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: Optional[str] = None,
    author: Optional[str] = None,
    subject_id: Optional[int] = 1,
    metadata: Optional[str] = None  # Có thể là None hoặc chuỗi JSON
):
    """
    Upload a PDF file for plagiarism detection processing.
    
    The file will be processed through:
    1. PDF text extraction
    2. Text preprocessing (tokenization, stopword removal)
    3. MinHash signature generation with datasketch
    4. Embedding generation with sentence transformers
    5. Storage in Milvus (vectors) and PostgreSQL (metadata)
    """
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )
    
    # Parse metadata if provided (có thể là None)
    parsed_metadata = {}
    if metadata is not None and metadata.strip():  # Check if metadata is not None and not empty
        try:
            # Handle both string and dict metadata
            if isinstance(metadata, str):
                # Try to clean up the JSON string
                metadata_str = metadata.strip()
                
                # Handle different quote types
                if metadata_str.startswith("'") and metadata_str.endswith("'"):
                    metadata_str = metadata_str[1:-1].replace("'", '"')
                elif metadata_str.startswith('"') and metadata_str.endswith('"'):
                    metadata_str = metadata_str[1:-1]
                
                # Parse JSON
                parsed_metadata = json.loads(metadata_str)
            else:
                parsed_metadata = metadata
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid metadata format. Use JSON format. Error: {str(e)}"
            )
    # Nếu metadata là None hoặc empty, parsed_metadata sẽ là {} (rỗng)
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        # Read and write file content
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        # Validate PDF
        validation_result = pdf_processor.validate_pdf(temp_file_path)
        if not validation_result['valid']:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid PDF file: {validation_result['error']}"
            )
        
        # Create document record in PostgreSQL
        doc_id = postgres_service.create_document_record(
            file_name=file.filename,
            file_path=temp_file_path,
            file_size=len(content),
            file_type='pdf',
            title=title,
            author=author,
            metadata=parsed_metadata
        )
        
        if not doc_id:
            raise HTTPException(
                status_code=500,
                detail="Failed to create document record"
            )
        
        # Process document in background
        def background_process():
            process_pdf_document(
                file_path=temp_file_path,
                file_name=file.filename,
                file_size=len(content),
                doc_id=doc_id,
                metadata=parsed_metadata
            )
        
        background_tasks.add_task(background_process)
        
        return UploadResponse(
            success=True,
            message="PDF uploaded successfully. Processing started in background.",
            document_id=doc_id,
            file_info={
                'filename': file.filename,
                'size': len(content),
                'pages': validation_result.get('total_pages'),
                'has_text': validation_result.get('has_text', False)
            }
        )
        
    except HTTPException:
        # Clean up temp file on error
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        raise
    
    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )


@app.get("/document-status/{doc_id}", response_model=DocumentStatus)
async def get_document_status(doc_id: int):
    """Get processing status of a document."""
    
    document = postgres_service.get_document_by_id(doc_id)
    
    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )
    
    return DocumentStatus(
        document_id=document['id'],
        status=document['status'],
        total_sentences=document['total_sentences'] or 0,
        processed_sentences=document['processed_sentences'] or 0,
        vector_count=document['vector_count'] or 0,
        error_message=document.get('error_message')
    )


@app.get("/document/{doc_id}")
async def get_document_details(doc_id: int):
    """Get detailed information about a document."""
    
    document = postgres_service.get_document_by_id(doc_id)
    
    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )
    
    sentences = postgres_service.get_document_sentences(doc_id)
    
    return {
        'document': document,
        'sentences_count': len(sentences),
        'sentences_sample': sentences[:5] if sentences else []  # Return first 5 sentences as sample
    }


@app.get("/documents")
async def list_documents(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """List documents with optional status filter."""
    
    conn = None
    try:
        conn = postgres_service.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM documents"
        params = []
        
        if status:
            query += " WHERE status = %s"
            params.append(status)
        
        query += " ORDER BY upload_date DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Get column names
        column_names = [desc[0] for desc in cursor.description]
        
        documents = []
        for row in results:
            doc_dict = dict(zip(column_names, row))
            # Parse metadata JSON
            if doc_dict.get('metadata'):
                try:
                    doc_dict['metadata'] = json.loads(doc_dict['metadata'])
                except:
                    pass
            documents.append(doc_dict)
        
        return {
            'documents': documents,
            'total': len(documents),
            'limit': limit,
            'offset': offset
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list documents: {str(e)}"
        )
    finally:
        if conn:
            conn.close()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    
    try:
        # Test PostgreSQL connection
        conn = postgres_service.get_connection()
        conn.close()
        
        # Test Milvus connection
        milvus_alias = doc_service.alias
        
        return {
            'status': 'healthy',
            'services': {
                'postgresql': 'connected',
                'milvus': 'connected',
                'pdf_processor': 'ready',
                'minhash_processor': 'ready',
                'embedding_model': 'loaded'
            }
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                'status': 'unhealthy',
                'error': str(e)
            }
        )


if __name__ == "__main__":
    uvicorn.run(
        "pdf_upload_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
