from __future__ import annotations

import json
from typing import List, Dict, Any, Optional

try:
    from datasketch import MinHash, MinHashLSH
except ImportError:
    raise ImportError(
        "Missing dependency 'datasketch'. Install it with: pip install datasketch"
    )

from .preprocessor import TextPreprocessor


class MinHashProcessor:
    """MinHash processor for generating and comparing document signatures."""
    
    def __init__(
        self,
        num_perm: int = 128,
        threshold: float = 0.8,
        min_words: int = 8
    ):
        """
        Initialize MinHash processor.
        
        Args:
            num_perm: Number of permutations for MinHash
            threshold: Similarity threshold for LSH
            min_words: Minimum words for valid sentences
        """
        self.num_perm = num_perm
        self.threshold = threshold
        self.preprocessor = TextPreprocessor(min_words=min_words)
        self.lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)
    
    def create_minhash(self, text: str) -> MinHash:
        """
        Create MinHash from text.
        
        Args:
            text: Input text
            
        Returns:
            MinHash object
        """
        # Preprocess text to get clean sentences
        processed_sentences = self.preprocessor.preprocess_text(text)
        
        # Create MinHash
        minhash = MinHash(num_perm=self.num_perm)
        
        # Add each sentence as a shingle
        for sentence in processed_sentences:
            # Split sentence into words (n-grams of words)
            words = sentence.split()
            
            # Add word n-grams (shingles) to MinHash
            for i in range(len(words) - 2 + 1):  # 2-grams
                shingle = ' '.join(words[i:i+2])
                minhash.update(shingle.encode('utf-8'))
        
        return minhash
    
    def create_minhash_from_sentences(self, sentences: List[str]) -> MinHash:
        """
        Create MinHash from preprocessed sentences.
        
        Args:
            sentences: List of preprocessed sentences
            
        Returns:
            MinHash object
        """
        minhash = MinHash(num_perm=self.num_perm)
        
        for sentence in sentences:
            words = sentence.split()
            for i in range(len(words) - 2 + 1):  # 2-grams
                shingle = ' '.join(words[i:i+2])
                minhash.update(shingle.encode('utf-8'))
        
        return minhash
    
    def get_minhash_signature(self, text: str) -> str:
        """
        Get compact string representation of MinHash.
        
        Args:
            text: Input text
            
        Returns:
            String representation of MinHash
        """
        minhash = self.create_minhash(text)
        # Convert to hex string for storage
        return ''.join([f'{x:02x}' for x in minhash.digest()])[:64]
    
    def get_minhash_signature_from_sentences(self, sentences: List[str]) -> str:
        """
        Get compact string representation from sentences.
        
        Args:
            sentences: List of preprocessed sentences
            
        Returns:
            String representation of MinHash
        """
        minhash = self.create_minhash_from_sentences(sentences)
        return ''.join([f'{x:02x}' for x in minhash.digest()])[:64]
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate Jaccard similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        minhash1 = self.create_minhash(text1)
        minhash2 = self.create_minhash(text2)
        
        return minhash1.jaccard(minhash2)
    
    def find_similar_documents(
        self, 
        query_text: str, 
        document_signatures: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Find documents similar to query text.
        
        Args:
            query_text: Query text
            document_signatures: Dict of {doc_id: minhash_signature}
            
        Returns:
            List of similar documents with similarity scores
        """
        query_minhash = self.create_minhash(query_text)
        similar_docs = []
        
        for doc_id, signature_str in document_signatures.items():
            # Reconstruct MinHash from signature (approximate)
            doc_minhash = MinHash(num_perm=self.num_perm)
            # This is a simplified approach - in practice you might store full MinHash objects
            # For now, we'll use the signature string directly for comparison
            
            # Calculate similarity (this is approximate)
            similarity = self._estimate_similarity_from_signature(
                query_minhash, signature_str
            )
            
            if similarity >= self.threshold:
                similar_docs.append({
                    'doc_id': doc_id,
                    'similarity': similarity
                })
        
        # Sort by similarity (descending)
        similar_docs.sort(key=lambda x: x['similarity'], reverse=True)
        return similar_docs
    
    def _estimate_similarity_from_signature(
        self, 
        query_minhash: MinHash, 
        signature_str: str
    ) -> float:
        """
        Estimate similarity from stored signature.
        This is a simplified approach - in production you'd store full MinHash objects.
        
        Args:
            query_minhash: Query MinHash
            signature_str: Stored signature string
            
        Returns:
            Estimated similarity
        """
        # This is a placeholder - in practice you'd need to reconstruct the MinHash
        # For now, return a default similarity
        # You could implement a more sophisticated approach here
        return 0.85  # Placeholder
    
    def process_document_for_upload(
        self, 
        text: str, 
        doc_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process document for upload with MinHash signature.
        
        Args:
            text: Document text
            doc_id: Optional document ID
            
        Returns:
            Dictionary with processed data including MinHash signature
        """
        # Preprocess document
        preprocess_result = self.preprocessor.preprocess_document(text)
        
        # Create MinHash signature
        minhash_signature = self.get_minhash_signature_from_sentences(
            preprocess_result['processed_sentences']
        )
        
        return {
            'doc_id': doc_id,
            'minhash_signature': minhash_signature,
            'processed_sentences': preprocess_result['processed_sentences'],
            'original_sentences': preprocess_result['original_sentences'],
            'stats': preprocess_result['stats'],
            'num_perm': self.num_perm,
            'threshold': self.threshold
        }
