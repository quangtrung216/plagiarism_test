"""
Service module for document embedding and similarity detection.
"""

from .embedding_service import DEk21HCMUTEEmbedding, EmbeddingService
from .document_processor import DocumentProcessor

__all__ = ['DEk21HCMUTEEmbedding', 'EmbeddingService', 'DocumentProcessor']

"""
Service module for document embedding and similarity detection.
"""

from .embedding_service import DEk21HCMUTEEmbedding, EmbeddingService
from .document_processor import DocumentProcessor
from .highlight_service import HighlightService

__all__ = ['DEk21HCMUTEEmbedding', 'EmbeddingService', 'DocumentProcessor', 'HighlightService']
