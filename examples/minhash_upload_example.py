"""
Example: Upload documents with MinHash signatures using datasketch
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from service.document_service import DocumentService


def main():
    """Example of uploading documents with MinHash processing."""
    
    # Initialize document service
    doc_service = DocumentService(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        collection_name="plagiarism_docs",
        num_perm=128,
        similarity_threshold=0.8,
        embedding_dim=384
    )
    
    # Sample documents
    documents = [
        {
            "id": 1,
            "subject_id": 101,
            "text": """
            Trí tuệ nhân tạo (AI) là một lĩnh vực của khoa học máy tính tập trung vào việc tạo ra các máy móc 
            thông minh có khả năng thực hiện các nhiệm vụ thường đòi hỏi trí tuệ con người. Các ứng dụng của AI 
            bao gồm xử lý ngôn ngữ tự nhiên, thị giác máy tính, học máy và robot học. Công nghệ AI đang phát triển 
            nhanh chóng và được ứng dụng trong nhiều lĩnh vực khác nhau như y tế, giáo dục, tài chính và sản xuất.
            """,
            "metadata": {"title": "Giới thiệu AI", "author": "Nguyễn Văn A", "year": 2023}
        },
        {
            "id": 2,
            "subject_id": 101,
            "text": """
            Machine learning là một nhánh của trí tuệ nhân tạo cho phép máy tính học hỏi từ dữ liệu mà không cần 
            được lập trình rõ ràng. Các thuật toán học máy có thể nhận dạng mẫu, đưa ra dự đoán và ra quyết định 
            dựa trên dữ liệu đầu vào. Có ba loại học máy chính: học có giám sát, học không giám sát và học tăng cường.
            """,
            "metadata": {"title": "Machine Learning", "author": "Trần Thị B", "year": 2023}
        },
        {
            "id": 3,
            "subject_id": 102,
            "text": """
            Xử lý ngôn ngữ tự nhiên (NLP) là lĩnh vực kết hợp giữa khoa học máy tính và ngôn ngữ học, tập trung vào 
            việc tạo ra các hệ thống có thể hiểu, diễn giải và tạo ra ngôn ngữ con người. Các ứng dụng NLP bao gồm 
            dịch thuật tự động, phân tích cảm xúc, chatbot và nhận dạng thực thể. Công nghệ NLP đã cải thiện đáng kể 
            nhờ sự phát triển của mô hình transformer và học sâu.
            """,
            "metadata": {"title": "NLP Overview", "author": "Lê Văn C", "year": 2023}
        }
    ]
    
    print("=== Upload Documents with MinHash ===")
    
    # Upload documents
    for doc in documents:
        print(f"\nUploading document {doc['id']}: {doc['metadata']['title']}")
        
        try:
            result = doc_service.upload_document(
                text=doc['text'],
                subject_id=doc['subject_id'],
                doc_id=doc['id'],
                metadata=doc['metadata']
            )
            
            print(f"✓ Upload successful!")
            print(f"  - MinHash signature: {result['processed_doc']['minhash_signature'][:16]}...")
            print(f"  - Processed sentences: {result['processed_doc']['stats']['final_sentences']}")
            print(f"  - Embedding dimension: {len(result['processed_doc']['document_embedding'])}")
            
        except Exception as e:
            print(f"✗ Upload failed: {e}")
    
    print("\n=== Upload Document as Chunks ===")
    
    # Upload a longer document as chunks
    long_document = {
        "id": 4,
        "subject_id": 103,
        "text": """
        Học sâu (Deep Learning) là một tập con của học máy sử dụng mạng nơ-ron nhân tạo với nhiều lớp ẩn.
        Các mạng học sâu có thể học các biểu diễn dữ liệu phức tạp thông qua nhiều cấp độ trừu tượng.
        Kiến trúc phổ biến trong học sâu bao gồm Mạng nơ-ron tích chập (CNN) cho xử lý ảnh,
        Mạng nơ-ron tuần hoàn (RNN) cho dữ liệu chuỗi thời gian, và Transformer cho xử lý ngôn ngữ.
        
        CNN được sử dụng rộng rãi trong nhận dạng hình ảnh và thị giác máy tính. Các lớp tích chập
        có thể phát hiện các đặc trưng địa phương như cạnh, góc và kết cấu, trong khi các lớp kết nối
        đầy đủ học các mối quan hệ cấp cao hơn.
        
        RNN và các biến thể như LSTM và GRU được thiết kế để xử lý dữ liệu tuần tự như văn bản
        và chuỗi thời gian. Chúng có thể ghi nhớ thông tin từ các bước thời gian trước đó và sử dụng
        nó để ảnh hưởng đến đầu ra hiện tại.
        
        Transformer, được giới thiệu trong bài báo "Attention Is All You Need", đã cách mạng hóa
        lĩnh vực xử lý ngôn ngữ tự nhiên. Cơ chế attention cho phép mô hình tập trung vào các phần
        quan trọng của đầu vào khi tạo ra đầu ra, giúp cải thiện hiệu suất trong các nhiệm vụ như
        dịch thuật, tóm tắt văn bản và trả lời câu hỏi.
        """,
        "metadata": {"title": "Deep Learning Guide", "author": "Phạm Văn D", "year": 2023}
    }
    
    print(f"Uploading document {long_document['id']} as chunks...")
    
    try:
        chunk_result = doc_service.upload_document_chunks(
            text=long_document['text'],
            subject_id=long_document['subject_id'],
            doc_id=long_document['id'],
            chunk_size=3,  # 3 sentences per chunk
            metadata=long_document['metadata']
        )
        
        print(f"✓ Chunk upload successful!")
        print(f"  - Number of chunks: {chunk_result['num_chunks']}")
        print(f"  - Chunk IDs: {chunk_result['chunk_ids']}")
        
        for i, chunk in enumerate(chunk_result['chunks']):
            print(f"  - Chunk {i+1}: {chunk['minhash_signature'][:16]}... ({len(chunk['sentences'])} sentences)")
            
    except Exception as e:
        print(f"✗ Chunk upload failed: {e}")
    
    print("\n=== Search Similar Documents ===")
    
    # Search for similar documents
    query_text = """
    Trí tuệ nhân tạo và học máy là công nghệ đang phát triển nhanh. Các thuật toán AI có thể học từ dữ liệu
    và thực hiện các nhiệm vụ thông minh như nhận dạng hình ảnh và xử lý ngôn ngữ tự nhiên.
    """
    
    print(f"Query: {query_text.strip()}")
    
    try:
        similar_docs = doc_service.find_similar_documents(
            query_text=query_text,
            subject_id=None,  # Search across all subjects
            limit=5,
            similarity_threshold=0.5
        )
        
        print(f"\nFound {len(similar_docs)} similar documents:")
        
        for i, doc in enumerate(similar_docs, 1):
            print(f"{i}. Document ID: {doc['doc_id']}")
            print(f"   Subject ID: {doc['subject_id']}")
            print(f"   Similarity: {doc['similarity']:.3f}")
            print(f"   MinHash: {doc['minhash_signature'][:16]}...")
            print(f"   Metadata: {doc['metadata']}")
            print()
            
    except Exception as e:
        print(f"✗ Search failed: {e}")
    
    print("\n=== MinHash Similarity Comparison ===")
    
    # Direct MinHash similarity comparison
    text1 = documents[0]['text']  # AI introduction
    text2 = documents[1]['text']  # Machine learning
    
    similarity = doc_service.minhash_processor.calculate_similarity(text1, text2)
    print(f"Similarity between doc 1 and doc 2: {similarity:.3f}")
    
    text3 = """
    Công nghệ thông tin bao gồm phần cứng, phần mềm và mạng lưới truyền thông.
        Việc phát triển công nghệ thông tin đã thay đổi hoàn toàn cách chúng ta làm việc và giao tiếp.
    """
    similarity2 = doc_service.minhash_processor.calculate_similarity(text1, text3)
    print(f"Similarity between doc 1 and unrelated text: {similarity2:.3f}")


if __name__ == "__main__":
    main()
