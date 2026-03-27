"""
Example: API integration for document upload with MinHash
This example shows how to integrate the MinHash functionality into a web API.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from service.document_service import DocumentService
from text_process.minhash_processor import MinHashProcessor


class PlagiarismAPI:
    """API wrapper for plagiarism detection with MinHash."""
    
    def __init__(self):
        """Initialize the API service."""
        self.doc_service = DocumentService()
        self.minhash_processor = MinHashProcessor()
    
    def upload_document(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Upload document endpoint.
        
        Expected request format:
        {
            "text": "Document content",
            "subject_id": 101,
            "doc_id": 123,
            "metadata": {"title": "Document Title", "author": "Author"},
            "chunk_size": 5  # Optional, for chunked upload
        }
        """
        try:
            text = request_data.get("text", "")
            subject_id = request_data.get("subject_id")
            doc_id = request_data.get("doc_id")
            metadata = request_data.get("metadata", {})
            chunk_size = request_data.get("chunk_size", 0)
            
            if not text or not subject_id or not doc_id:
                return {
                    "success": False,
                    "error": "Missing required fields: text, subject_id, doc_id"
                }
            
            # Choose upload method based on chunk_size
            if chunk_size and chunk_size > 0:
                result = self.doc_service.upload_document_chunks(
                    text=text,
                    subject_id=subject_id,
                    doc_id=doc_id,
                    chunk_size=chunk_size,
                    metadata=metadata
                )
                
                response = {
                    "success": True,
                    "message": "Document uploaded as chunks",
                    "doc_id": doc_id,
                    "num_chunks": result["num_chunks"],
                    "chunk_ids": result["chunk_ids"],
                    "collection_name": result["collection_name"]
                }
            else:
                result = self.doc_service.upload_document(
                    text=text,
                    subject_id=subject_id,
                    doc_id=doc_id,
                    metadata=metadata
                )
                
                response = {
                    "success": True,
                    "message": "Document uploaded successfully",
                    "doc_id": doc_id,
                    "minhash_signature": result["processed_doc"]["minhash_signature"],
                    "sentence_count": result["processed_doc"]["stats"]["final_sentences"],
                    "collection_name": result["collection_name"]
                }
            
            return response
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_similar(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search similar documents endpoint.
        
        Expected request format:
        {
            "query_text": "Text to search for",
            "subject_id": 101,  # Optional
            "limit": 10,        # Optional
            "threshold": 0.7    # Optional
        }
        """
        try:
            query_text = request_data.get("query_text", "")
            subject_id = request_data.get("subject_id")
            limit = request_data.get("limit", 10)
            threshold = request_data.get("threshold", 0.7)
            
            if not query_text:
                return {
                    "success": False,
                    "error": "Missing required field: query_text"
                }
            
            similar_docs = self.doc_service.find_similar_documents(
                query_text=query_text,
                subject_id=subject_id,
                limit=limit,
                similarity_threshold=threshold
            )
            
            response = {
                "success": True,
                "query": query_text[:100] + "..." if len(query_text) > 100 else query_text,
                "results": similar_docs,
                "count": len(similar_docs),
                "filters": {
                    "subject_id": subject_id,
                    "threshold": threshold,
                    "limit": limit
                }
            }
            
            return response
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_document(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get document by ID endpoint.
        
        Expected request format:
        {
            "doc_id": 123
        }
        """
        try:
            doc_id = request_data.get("doc_id")
            
            if not doc_id:
                return {
                    "success": False,
                    "error": "Missing required field: doc_id"
                }
            
            document = self.doc_service.get_document_by_id(doc_id)
            
            if not document:
                return {
                    "success": False,
                    "error": f"Document {doc_id} not found"
                }
            
            return {
                "success": True,
                "document": document
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def compare_documents(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare two documents directly using MinHash.
        
        Expected request format:
        {
            "text1": "First document text",
            "text2": "Second document text"
        }
        """
        try:
            text1 = request_data.get("text1", "")
            text2 = request_data.get("text2", "")
            
            if not text1 or not text2:
                return {
                    "success": False,
                    "error": "Missing required fields: text1, text2"
                }
            
            similarity = self.minhash_processor.calculate_similarity(text1, text2)
            
            # Also get signatures for reference
            sig1 = self.minhash_processor.get_minhash_signature(text1)
            sig2 = self.minhash_processor.get_minhash_signature(text2)
            
            return {
                "success": True,
                "similarity": float(similarity),
                "similarity_percentage": f"{similarity * 100:.1f}%",
                "signature1": sig1,
                "signature2": sig2,
                "threshold_used": self.minhash_processor.threshold
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def batch_upload(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Batch upload multiple documents.
        
        Expected request format:
        {
            "documents": [
                {
                    "text": "Document 1 content",
                    "subject_id": 101,
                    "doc_id": 1,
                    "metadata": {...}
                },
                ...
            ]
        }
        """
        try:
            documents = request_data.get("documents", [])
            
            if not documents:
                return {
                    "success": False,
                    "error": "No documents provided"
                }
            
            results = []
            successful_uploads = 0
            failed_uploads = 0
            
            for i, doc in enumerate(documents):
                result = self.upload_document(doc)
                results.append({
                    "index": i,
                    "doc_id": doc.get("doc_id"),
                    "result": result
                })
                
                if result["success"]:
                    successful_uploads += 1
                else:
                    failed_uploads += 1
            
            return {
                "success": True,
                "message": f"Batch upload completed: {successful_uploads} successful, {failed_uploads} failed",
                "total_documents": len(documents),
                "successful_uploads": successful_uploads,
                "failed_uploads": failed_uploads,
                "results": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


def demo_api_usage():
    """Demonstrate API usage with sample requests."""
    
    api = PlagiarismAPI()
    
    print("=== API Demo: Document Upload ===")
    
    # Upload a document
    upload_request = {
        "text": """
        Machine learning là một phương pháp phân tích dữ liệu tự động hóa việc xây dựng mô hình phân tích.
        Đây là một nhánh của trí tuệ nhân tạo dựa trên ý tưởng rằng các hệ thống có thể học từ dữ liệu,
        nhận dạng các mẫu và đưa ra quyết định với sự can thiệp tối thiểu của con người.
        """,
        "subject_id": 101,
        "doc_id": 1001,
        "metadata": {
            "title": "Machine Learning Introduction",
            "author": "AI Expert",
            "course": "CS101"
        }
    }
    
    upload_response = api.upload_document(upload_request)
    print("Upload Response:", json.dumps(upload_response, indent=2, ensure_ascii=False))
    
    print("\n=== API Demo: Similar Documents Search ===")
    
    # Search for similar documents
    search_request = {
        "query_text": "Trí tuệ nhân tạo và học máy giúp máy tính học từ dữ liệu",
        "subject_id": 101,
        "limit": 5,
        "threshold": 0.5
    }
    
    search_response = api.search_similar(search_request)
    print("Search Response:", json.dumps(search_response, indent=2, ensure_ascii=False))
    
    print("\n=== API Demo: Document Comparison ===")
    
    # Compare two documents
    compare_request = {
        "text1": "Machine learning là một nhánh của AI giúp máy tính học từ dữ liệu.",
        "text2": "Học máy là một lĩnh vực của trí tuệ nhân tạo cho phép hệ thống tự học."
    }
    
    compare_response = api.compare_documents(compare_request)
    print("Compare Response:", json.dumps(compare_response, indent=2, ensure_ascii=False))
    
    print("\n=== API Demo: Batch Upload ===")
    
    # Batch upload multiple documents
    batch_request = {
        "documents": [
            {
                "text": "Deep learning sử dụng mạng nơ-ron sâu để học các biểu diễn phức tạp.",
                "subject_id": 102,
                "doc_id": 2001,
                "metadata": {"title": "Deep Learning", "course": "CS102"}
            },
            {
                "text": "Neural networks mô phỏng cách hoạt động của nơ-ron trong não bộ con người.",
                "subject_id": 102,
                "doc_id": 2002,
                "metadata": {"title": "Neural Networks", "course": "CS102"}
            }
        ]
    }
    
    batch_response = api.batch_upload(batch_request)
    print("Batch Response:", json.dumps(batch_response, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    demo_api_usage()
