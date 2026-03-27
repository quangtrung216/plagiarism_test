"""
Simple test to check Milvus upload
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from service.document_service import DocumentService
import json

def test_milvus_upload():
    """Test Milvus upload with simple data"""
    
    print("🔍 Testing Milvus upload...")
    
    try:
        # Initialize service
        doc_service = DocumentService()
        
        # Simple test data
        test_text = "Đây là một câu test để kiểm tra MinHash và embedding."
        test_metadata = {"test": True, "source": "debug"}
        
        print(f"📝 Test text: {test_text}")
        print(f"📊 Embedding dim: {doc_service.embedding_dim}")
        
        # Process document
        processed = doc_service.process_document(
            text=test_text,
            subject_id=1,
            doc_id=999,  # Test ID
            metadata=test_metadata
        )
        
        print(f"✅ Processed: {len(processed.get('processed_sentences', []))} sentences")
        print(f"🔍 MinHash: {processed.get('minhash_signature', '')[:50]}...")
        
        # Upload to Milvus
        upload_result = doc_service.upload_document(
            text=test_text,
            subject_id=1,
            doc_id=999,
            metadata=test_metadata
        )
        
        print(f"🚀 Upload result: {upload_result}")
        print("✅ Milvus upload successful!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_milvus_upload()
