"""
Embedding service using DEk21_hcmute_embedding model for Vietnamese text.
"""

import os
import logging
from typing import List, Union, Optional
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    raise ImportError(
        "Missing dependency 'sentence-transformers'. Install it with: pip install sentence-transformers"
    )

try:
    import torch
except ImportError:
    raise ImportError(
        "Missing dependency 'torch'. Install it with: pip install torch"
    )


class DEk21HCMUTEEmbedding:
    """
    Embedding service using DEk21_hcmute_embedding model for Vietnamese text.
    
    This class provides functionality to embed Vietnamese text sentences using
    the DEk21_hcmute_embedding model, which is specifically trained for Vietnamese
    text processing and plagiarism detection.
    """
    
    def __init__(self, model_name: str = "DEk21_hcmute_embedding", device: Optional[str] = None):
        """
        Initialize the embedding service.
        
        Args:
            model_name: Name of the embedding model
            device: Device to run the model on ('cuda', 'cpu', or None for auto-detection)
        """
        self.model_name = model_name
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.logger = logging.getLogger(__name__)
        
        try:
            self.model = SentenceTransformer(model_name)
            self.model.to(self.device)
            self.logger.info(f"Model '{model_name}' loaded successfully on device: {self.device}")
        except Exception as e:
            self.logger.error(f"Failed to load model '{model_name}': {e}")
            # Fallback to a multilingual model if the specific model is not available
            self.logger.info("Falling back to multilingual model...")
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            self.model.to(self.device)
    
    def embed_sentences(self, sentences: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Embed a list of sentences into vectors.
        
        Args:
            sentences: List of preprocessed sentences to embed
            batch_size: Batch size for processing
            
        Returns:
            numpy array of embeddings with shape (len(sentences), embedding_dim)
        """
        if not sentences:
            return np.array([])
        
        try:
            # Filter out empty sentences
            valid_sentences = [sent.strip() for sent in sentences if sent.strip()]
            
            if not valid_sentences:
                return np.array([])
            
            # Generate embeddings
            embeddings = self.model.encode(
                valid_sentences,
                batch_size=batch_size,
                show_progress_bar=True,
                convert_to_numpy=True,
                normalize_embeddings=True  # Normalize for cosine similarity
            )
            
            self.logger.info(f"Successfully embedded {len(valid_sentences)} sentences")
            return embeddings
            
        except Exception as e:
            self.logger.error(f"Error embedding sentences: {e}")
            raise
    
    def embed_single_sentence(self, sentence: str) -> np.ndarray:
        """
        Embed a single sentence into a vector.
        
        Args:
            sentence: Single sentence to embed
            
        Returns:
            numpy array representing the embedding
        """
        if not sentence or not sentence.strip():
            return np.array([])
        
        try:
            embedding = self.model.encode(
                sentence.strip(),
                convert_to_numpy=True,
                normalize_embeddings=True
            )
            return embedding
        except Exception as e:
            self.logger.error(f"Error embedding sentence: {e}")
            raise
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Cosine similarity score (0-1)
        """
        try:
            # Ensure embeddings are normalized
            if embedding1.ndim == 1:
                embedding1 = embedding1.reshape(1, -1)
            if embedding2.ndim == 1:
                embedding2 = embedding2.reshape(1, -1)
            
            # Compute cosine similarity
            similarity = np.dot(embedding1, embedding2.T)[0, 0]
            return float(similarity)
        except Exception as e:
            self.logger.error(f"Error computing similarity: {e}")
            return 0.0
    
    def find_similar_sentences(
        self, 
        query_embedding: np.ndarray, 
        corpus_embeddings: np.ndarray,
        threshold: float = 0.7,
        top_k: int = 10
    ) -> List[tuple]:
        """
        Find sentences similar to the query embedding.
        
        Args:
            query_embedding: Embedding of the query sentence
            corpus_embeddings: Embeddings of the corpus sentences
            threshold: Minimum similarity threshold
            top_k: Maximum number of results to return
            
        Returns:
            List of tuples (index, similarity_score) sorted by similarity
        """
        try:
            if query_embedding.ndim == 1:
                query_embedding = query_embedding.reshape(1, -1)
            
            # Compute similarities
            similarities = np.dot(corpus_embeddings, query_embedding.T).flatten()
            
            # Filter by threshold and get top_k
            valid_indices = np.where(similarities >= threshold)[0]
            
            if len(valid_indices) == 0:
                return []
            
            # Sort by similarity
            sorted_indices = valid_indices[np.argsort(similarities[valid_indices])[::-1]]
            
            # Get top_k results
            top_indices = sorted_indices[:top_k]
            results = [(int(idx), float(similarities[idx])) for idx in top_indices]
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error finding similar sentences: {e}")
            return []
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.
        
        Returns:
            Dimension of the embedding vectors
        """
        try:
            # Create a dummy embedding to get the dimension
            dummy_embedding = self.embed_single_sentence("test")
            return dummy_embedding.shape[0] if dummy_embedding.ndim > 0 else 0
        except Exception as e:
            self.logger.error(f"Error getting embedding dimension: {e}")
            return 0


class EmbeddingService:
    """
    High-level service for document embedding operations.
    """
    
    def __init__(self, model_name: str = "DEk21_hcmute_embedding"):
        """
        Initialize the embedding service.
        
        Args:
            model_name: Name of the embedding model to use
        """
        self.embedding_model = DEk21HCMUTEEmbedding(model_name)
        self.logger = logging.getLogger(__name__)
    
    def process_document_embeddings(self, processed_sentences: List[str]) -> dict:
        """
        Process embeddings for a list of preprocessed sentences.
        
        Args:
            processed_sentences: List of preprocessed sentences from text processing
            
        Returns:
            Dictionary containing embeddings and metadata
        """
        try:
            if not processed_sentences:
                return {
                    'embeddings': np.array([]),
                    'sentences': [],
                    'stats': {
                        'total_sentences': 0,
                        'embedded_sentences': 0,
                        'embedding_dimension': 0
                    }
                }
            
            # Generate embeddings
            embeddings = self.embedding_model.embed_sentences(processed_sentences)
            
            # Get embedding dimension
            embedding_dim = self.embedding_model.get_embedding_dimension()
            
            result = {
                'embeddings': embeddings,
                'sentences': processed_sentences,
                'stats': {
                    'total_sentences': len(processed_sentences),
                    'embedded_sentences': len(embeddings),
                    'embedding_dimension': embedding_dim
                }
            }
            
            self.logger.info(f"Processed embeddings for {len(embeddings)} sentences")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing document embeddings: {e}")
            raise
    
    def compare_documents(self, doc1_embeddings: np.ndarray, doc2_embeddings: np.ndarray) -> dict:
        """
        Compare two documents using their embeddings.
        
        Args:
            doc1_embeddings: Embeddings of document 1
            doc2_embeddings: Embeddings of document 2
            
        Returns:
            Dictionary containing comparison results
        """
        try:
            if len(doc1_embeddings) == 0 or len(doc2_embeddings) == 0:
                return {
                    'average_similarity': 0.0,
                    'max_similarity': 0.0,
                    'similar_sentence_pairs': []
                }
            
            # Compute all pairwise similarities
            similarities = np.dot(doc1_embeddings, doc2_embeddings.T)
            
            # Get statistics
            max_similarity = float(np.max(similarities))
            average_similarity = float(np.mean(similarities))
            
            # Find similar sentence pairs above threshold
            threshold = 0.7
            similar_pairs = []
            
            for i in range(len(doc1_embeddings)):
                for j in range(len(doc2_embeddings)):
                    sim = similarities[i, j]
                    if sim >= threshold:
                        similar_pairs.append({
                            'doc1_sentence_idx': i,
                            'doc2_sentence_idx': j,
                            'similarity': float(sim)
                        })
            
            # Sort by similarity
            similar_pairs.sort(key=lambda x: x['similarity'], reverse=True)
            
            return {
                'average_similarity': average_similarity,
                'max_similarity': max_similarity,
                'similar_sentence_pairs': similar_pairs[:20]  # Top 20 pairs
            }
            
        except Exception as e:
            self.logger.error(f"Error comparing documents: {e}")
            raise
