from __future__ import annotations

import json
from typing import List, Dict, Any, Optional, Tuple

from text_process.minhash_processor import MinHashProcessor
from text_process.preprocessor import TextPreprocessor
from db.milvus import connect_milvus
from orchestation.milvus_schema import ensure_collection_and_index

try:
    from sentence_transformers import SentenceTransformer
    from pymilvus import Collection
    import numpy as np
except ImportError as e:
    raise ImportError(
        f"Missing dependency: {e}. Install with: pip install sentence-transformers pymilvus numpy"
    )

from service.embedding_service import DEk21HCMUTEEmbedding


class DocumentService:
    """Service for uploading and managing documents with MinHash and embeddings."""
    
    def __init__(
        self,
        model_name: str = "huyydangg/DEk21_hcmute_embedding",  # Model từ HuggingFace
        collection_name: str = "plagiarism_docs_2024",
        num_perm: int = 128,
        similarity_threshold: float = 0.8,
        embedding_dim: int = 768  # Dimension cho DEk21_hcmute_embedding
    ):
        """
        Initialize document service.
        
        Args:
            model_name: Sentence transformer model name
            collection_name: Milvus collection name
            num_perm: Number of permutations for MinHash
            similarity_threshold: Similarity threshold
            embedding_dim: Embedding dimension
        """
        self.model_name = model_name
        self.collection_name = collection_name
        self.embedding_dim = embedding_dim
        
        # Initialize processors
        self.minhash_processor = MinHashProcessor(
            num_perm=num_perm,
            threshold=similarity_threshold
        )
        self.text_preprocessor = TextPreprocessor()
        
        # Load embedding model
        self.embedding_model = DEk21HCMUTEEmbedding(model_name)
        
        # Get embedding dimension from model
        test_embedding = self.embedding_model.embed_sentences(["test"])
        self.embedding_dim = len(test_embedding[0]) if len(test_embedding) > 0 else 768
        
        # Connect to Milvus and ensure collection exists
        self.alias = connect_milvus()
        self.collection = ensure_collection_and_index(
            collection_name=collection_name,
            dim=self.embedding_dim,  # Dùng dimension thực tế từ model
            alias=self.alias
        )
    
    def generate_embeddings(self, sentences: List[str]) -> List[List[float]]:
        """
        Generate embeddings for sentences.
        
        Args:
            sentences: List of sentences
            
        Returns:
            List of embedding vectors
        """
        if not sentences:
            return []
        
        embeddings = self.embedding_model.embed_sentences(sentences)
        return embeddings.tolist()
    
    def process_document(
        self, 
        text: str, 
        subject_id: int,
        doc_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process document with MinHash and embeddings.
        
        Args:
            text: Document text
            subject_id: Subject ID for filtering
            doc_id: Document ID (optional)
            metadata: Additional metadata
            
        Returns:
            Processed document data
        """
        # Process with MinHash
        minhash_result = self.minhash_processor.process_document_for_upload(text, doc_id)
        
        # Generate embeddings for processed sentences
        embeddings = self.generate_embeddings(minhash_result['processed_sentences'])
        
        # Calculate document-level embedding (average of sentence embeddings)
        if embeddings:
            doc_embedding = np.mean(embeddings, axis=0).tolist()
        else:
            doc_embedding = [0.0] * self.embedding_dim
        
        return {
            'doc_id': doc_id,
            'subject_id': subject_id,
            'minhash_signature': minhash_result['minhash_signature'],
            'document_embedding': doc_embedding,
            'sentence_embeddings': embeddings,
            'processed_sentences': minhash_result['processed_sentences'],
            'original_sentences': minhash_result['original_sentences'],
            'stats': minhash_result['stats'],
            'metadata': metadata or {}
        }
    
    def upload_document(
        self,
        text: str,
        subject_id: int,
        doc_id: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Upload document to Milvus with MinHash and embeddings.
        
        Args:
            text: Document text
            subject_id: Subject ID for filtering
            doc_id: Document ID
            metadata: Additional metadata
            
        Returns:
            Upload result
        """
        # Process document
        processed_doc = self.process_document(
            text=text,
            subject_id=subject_id,
            doc_id=doc_id,
            metadata=metadata
        )
        
        # Prepare data for Milvus insertion
        data = [
            [doc_id],
            [subject_id],
            [processed_doc['minhash_signature']],
            [processed_doc['document_embedding']],
            [json.dumps(processed_doc['metadata'])]
        ]
        
        # Insert into Milvus
        insert_result = self.collection.insert(data)
        
        return {
            'doc_id': doc_id,
            'insert_result': insert_result,
            'processed_doc': processed_doc,
            'collection_name': self.collection_name
        }
    
    def upload_document_chunks(
        self,
        text: str,
        subject_id: int,
        doc_id: int,
        chunk_size: int = 5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Upload document as chunks to Milvus.
        
        Args:
            text: Document text
            subject_id: Subject ID for filtering
            doc_id: Document ID
            chunk_size: Number of sentences per chunk
            metadata: Additional metadata
            
        Returns:
            Upload result with chunk information
        """
        # Process document
        processed_doc = self.process_document(
            text=text,
            subject_id=subject_id,
            doc_id=doc_id,
            metadata=metadata
        )
        
        sentences = processed_doc['processed_sentences']
        sentence_embeddings = processed_doc['sentence_embeddings']
        
        # Create chunks
        chunks = []
        chunk_ids = []
        
        for i in range(0, len(sentences), chunk_size):
            chunk_sentences = sentences[i:i+chunk_size]
            chunk_embeddings = sentence_embeddings[i:i+chunk_size]
            
            # Calculate chunk embedding (average)
            if chunk_embeddings:
                chunk_embedding = np.mean(chunk_embeddings, axis=0).tolist()
            else:
                chunk_embedding = [0.0] * self.embedding_dim
            
            # Create chunk text for MinHash
            chunk_text = ' '.join(chunk_sentences)
            chunk_minhash = self.minhash_processor.get_minhash_signature(chunk_text)
            
            chunk_id = f"{doc_id}_chunk_{i//chunk_size}"
            chunk_ids.append(chunk_id)
            
            chunks.append({
                'chunk_id': chunk_id,
                'chunk_text': chunk_text,
                'chunk_embedding': chunk_embedding,
                'minhash_signature': chunk_minhash,
                'sentences': chunk_sentences
            })
        
        # Prepare data for Milvus insertion
        ids = [int(chunk_id.split('_')[2]) * 1000 + int(chunk_id.split('_')[0]) for chunk_id in chunk_ids]
        subject_ids = [subject_id] * len(chunks)
        minhash_signatures = [chunk['minhash_signature'] for chunk in chunks]
        embeddings = [chunk['chunk_embedding'] for chunk in chunks]
        metadata_list = [
            json.dumps({
                **metadata,
                'doc_id': doc_id,
                'chunk_index': i,
                'chunk_sentences': chunk['sentences'],
                'chunk_text': chunk['chunk_text']
            })
            for i, chunk in enumerate(chunks)
        ]
        
        # Insert chunks into Milvus
        data = [ids, subject_ids, minhash_signatures, embeddings, metadata_list]
        insert_result = self.collection.insert(data)
        
        return {
            'doc_id': doc_id,
            'num_chunks': len(chunks),
            'chunk_ids': chunk_ids,
            'insert_result': insert_result,
            'chunks': chunks,
            'collection_name': self.collection_name
        }
    
    def find_similar_documents(
        self,
        query_text: str,
        subject_id: Optional[int] = None,
        limit: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Find similar documents using MinHash filtering and vector search.
        
        Args:
            query_text: Query text
            subject_id: Optional subject filter
            limit: Maximum number of results
            similarity_threshold: Minimum similarity threshold
            
        Returns:
            List of similar documents
        """
        # Process query
        query_processed = self.process_document(
            text=query_text,
            subject_id=subject_id or 0,
            doc_id=None
        )
        
        # Build search expression
        expr_parts = []
        if subject_id is not None:
            expr_parts.append(f"subject_id == {subject_id}")
        
        # Add MinHash similarity filter (simplified - in practice you'd use LSH)
        # For now, we'll rely on vector similarity
        expr = " and ".join(expr_parts) if expr_parts else None
        
        # Search parameters
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10}
        }
        
        # Perform vector search
        results = self.collection.search(
            data=[query_processed['document_embedding']],
            anns_field="content_vector",
            param=search_params,
            limit=limit,
            expr=expr,
            output_fields=["id", "subject_id", "minhash", "metadata"]
        )
        
        # Format results
        similar_docs = []
        for hit in results[0]:
            if hit.score >= similarity_threshold:
                metadata = json.loads(hit.entity.get('metadata', '{}'))
                similar_docs.append({
                    'doc_id': hit.entity.get('id'),
                    'subject_id': hit.entity.get('subject_id'),
                    'similarity': float(hit.score),
                    'minhash_signature': hit.entity.get('minhash'),
                    'metadata': metadata
                })
        
        return similar_docs
    
    def get_document_by_id(self, doc_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve document by ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document data or None
        """
        results = self.collection.query(
            expr=f"id == {doc_id}",
            output_fields=["id", "subject_id", "minhash", "content_vector", "metadata"],
            limit=1
        )
        
        if not results:
            return None
        
        result = results[0]
        metadata = json.loads(result.get('metadata', '{}'))
        
        return {
            'doc_id': result.get('id'),
            'subject_id': result.get('subject_id'),
            'minhash_signature': result.get('minhash'),
            'embedding': result.get('content_vector'),
            'metadata': metadata
        }
