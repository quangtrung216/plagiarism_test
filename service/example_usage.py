#!/usr/bin/env python3
"""
Example usage of the embedding service for document processing and plagiarism detection.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from service import DocumentProcessor, EmbeddingService, DEk21HCMUTEEmbedding


def example_basic_embedding():
    """Example of basic embedding functionality."""
    print("=== Basic Embedding Example ===")
    
    # Initialize embedding service
    embedding_service = EmbeddingService()
    
    # Sample Vietnamese sentences
    sentences = [
        "Trí tuệ nhân tạo đang thay đổi thế giới công nghệ",
        "Học máy là một nhánh của trí tuệ nhân tạo",
        "Phát triển phần mềm đòi hỏi kỹ năng lập trình tốt",
        "Ngôn ngữ lập trình Python rất phổ biến trong khoa học dữ liệu",
        "Xử lý ngôn ngữ tự nhiên là lĩnh vực nghiên cứu quan trọng"
    ]
    
    print(f"Processing {len(sentences)} sentences...")
    
    # Generate embeddings
    result = embedding_service.process_document_embeddings(sentences)
    
    print(f"Embedding dimension: {result['stats']['embedding_dimension']}")
    print(f"Successfully embedded {result['stats']['embedded_sentences']} sentences")
    
    # Show first embedding
    if len(result['embeddings']) > 0:
        print(f"First embedding shape: {result['embeddings'][0].shape}")
        print(f"First 5 values: {result['embeddings'][0][:5]}")


def example_document_processing():
    """Example of complete document processing pipeline."""
    print("\n=== Document Processing Example ===")
    
    # Initialize document processor
    processor = DocumentProcessor(min_words=5)
    
    # Sample Vietnamese document
    sample_text = """
    Giáo dục đại học Việt Nam đang đối mặt với nhiều thách thức trong bối cảnh hội nhập quốc tế.
    Các trường đại học cần đổi mới chương trình đào tạo để đáp ứng yêu cầu của thị trường lao động.
    Chất lượng giảng dạy và nghiên cứu khoa học là yếu tố then chốt để nâng cao uy tín.
    Sinh viên cần được trang bị kiến thức chuyên môn và kỹ năng mềm.
    Hợp tác quốc tế trong giáo dục đang ngày càng được chú trọng.
    """
    
    print("Processing sample Vietnamese document...")
    
    # Process document
    result = processor.process_text_document(sample_text)
    
    # Display results
    stats = result['processing_stats']
    print(f"Original text length: {stats['original_text_length']} characters")
    print(f"Original sentences: {stats['original_sentences']}")
    print(f"Processed sentences: {stats['processed_sentences']}")
    print(f"Embedded sentences: {stats['embedded_sentences']}")
    print(f"Embedding dimension: {stats['embedding_dimension']}")
    
    print("\nProcessed sentences:")
    for i, sent in enumerate(result['preprocessing_result']['processed_sentences']):
        print(f"{i+1}. {sent}")


def example_document_comparison():
    """Example of document comparison for plagiarism detection."""
    print("\n=== Document Comparison Example ===")
    
    processor = DocumentProcessor(min_words=5)
    
    # Two similar documents
    doc1 = """
    Trí tuệ nhân tạo là lĩnh vực công nghệ phát triển nhanh trong những năm gần đây.
    Các ứng dụng AI đang xuất hiện trong mọi khía cạnh của cuộc sống hàng ngày.
    Machine learning giúp máy tính học hỏi từ dữ liệu mà không cần lập trình tường minh.
    """
    
    doc2 = """
    Trí tuệ nhân tạo là một lĩnh vực công nghệ đang phát triển rất nhanh.
    Các ứng dụng của AI có mặt trong nhiều khía cạnh khác nhau của đời sống.
    Học máy cho phép máy tính học từ dữ liệu mà không cần lập trình rõ ràng.
    """
    
    print("Processing two similar documents...")
    
    # Process both documents
    result1 = processor.process_text_document(doc1)
    result2 = processor.process_text_document(doc2)
    
    # Compare documents
    comparison = processor.compare_documents(result1, result2)
    
    print(f"Document 1 sentences: {comparison['comparison_stats']['doc1_sentences']}")
    print(f"Document 2 sentences: {comparison['comparison_stats']['doc2_sentences']}")
    print(f"Maximum similarity: {comparison['comparison_stats']['max_similarity']:.4f}")
    print(f"Average similarity: {comparison['comparison_stats']['average_similarity']:.4f}")
    print(f"Similar sentence pairs found: {comparison['comparison_stats']['similar_pairs_found']}")
    
    # Show similar pairs
    similar_pairs = comparison['comparison_result']['similar_sentence_pairs']
    for i, pair in enumerate(similar_pairs[:3]):  # Show top 3
        print(f"\nSimilar Pair {i+1}:")
        print(f"  Doc1 Sentence {pair['doc1_sentence_idx']}: {result1['preprocessing_result']['processed_sentences'][pair['doc1_sentence_idx']]}")
        print(f"  Doc2 Sentence {pair['doc2_sentence_idx']}: {result2['preprocessing_result']['processed_sentences'][pair['doc2_sentence_idx']]}")
        print(f"  Similarity: {pair['similarity']:.4f}")


def example_pdf_processing():
    """Example of PDF document processing."""
    print("\n=== PDF Processing Example ===")
    
    processor = DocumentProcessor(min_words=5)
    
    # Example PDF path (replace with actual path)
    pdf_path = "sample_document.pdf"
    
    if Path(pdf_path).exists():
        try:
            print(f"Processing PDF: {pdf_path}")
            result = processor.process_pdf_document(pdf_path)
            
            stats = result['processing_stats']
            print(f"File: {stats['file_name']}")
            print(f"Size: {stats['file_size']} bytes")
            print(f"Original sentences: {stats['original_sentences']}")
            print(f"Processed sentences: {stats['processed_sentences']}")
            print(f"Embedded sentences: {stats['embedded_sentences']}")
            print(f"Embedding dimension: {stats['embedding_dimension']}")
            
        except Exception as e:
            print(f"Error processing PDF: {e}")
    else:
        print(f"PDF file not found: {pdf_path}")
        print("Please provide a valid PDF file path to test PDF processing")


def example_directory_processing():
    """Example of processing multiple documents in a directory."""
    print("\n=== Directory Processing Example ===")
    
    processor = DocumentProcessor(min_words=5)
    
    # Example directory path (replace with actual path)
    directory_path = "./documents"
    
    if Path(directory_path).exists():
        try:
            print(f"Processing directory: {directory_path}")
            results = processor.process_directory(directory_path, recursive=True)
            
            successful_results = [r for r in results if 'error' not in r]
            failed_results = [r for r in results if 'error' in r]
            
            print(f"Total files found: {len(results)}")
            print(f"Successfully processed: {len(successful_results)}")
            print(f"Failed to process: {len(failed_results)}")
            
            total_sentences = sum(r['processing_stats']['embedded_sentences'] for r in successful_results)
            print(f"Total embedded sentences: {total_sentences}")
            
            # Show summary for each successful file
            for result in successful_results:
                stats = result['processing_stats']
                print(f"  ✓ {stats['file_name']}: {stats['embedded_sentences']} sentences")
                
        except Exception as e:
            print(f"Error processing directory: {e}")
    else:
        print(f"Directory not found: {directory_path}")
        print("Please provide a valid directory path to test directory processing")


def example_plagiarism_detection():
    """Example of plagiarism detection workflow."""
    print("\n=== Plagiarism Detection Example ===")
    
    processor = DocumentProcessor(min_words=5)
    
    # Query document (suspected document)
    query_doc = """
    Phát triển bền vững là mục tiêu quan trọng trong thế kỷ 21.
    Các quốc gia cần hợp tác để giải quyết vấn đề biến đổi khí hậu.
    Năng lượng tái tạo là giải pháp cho tương lai xanh.
    Kinh tế tuần hoàn giúp giảm thiểu tác động tiêu cực đến môi trường.
    """
    
    # Corpus of documents to compare against
    corpus_docs = [
        """
        Phát triển bền vững là mục tiêu hàng đầu của nhiều quốc gia.
        Biến đổi khí hậu đòi hỏi sự hợp tác toàn cầu.
        Năng lượng sạch và tái tạo là tương lai của ngành năng lượng.
        Mô hình kinh tế tuần hoàn đang được áp dụng rộng rãi.
        """,
        """
        Công nghệ thông tin đang thay đổi cách chúng ta làm việc.
        Internet kết nối mọi người trên khắp thế giới.
        Trí tuệ nhân tạo mở ra nhiều cơ hội mới.
        """,
        """
        Phát triển bền vững đòi hỏi cân bằng giữa kinh tế và môi trường.
        Các quốc gia đang tìm kiếm giải pháp cho biến đổi khí hậu.
        Nguồn năng lượng tái tạo đang ngày càng phổ biến.
        """
    ]
    
    print("Processing query document...")
    query_result = processor.process_text_document(query_doc)
    
    print("Processing corpus documents...")
    corpus_results = []
    for i, doc in enumerate(corpus_docs):
        result = processor.process_text_document(doc)
        corpus_results.append(result)
        print(f"  Corpus document {i+1}: {result['processing_stats']['embedded_sentences']} sentences")
    
    # Find similar documents
    similar_docs = processor.find_similar_documents(
        query_result, 
        corpus_results, 
        similarity_threshold=0.5,
        top_k=3
    )
    
    print(f"\nFound {len(similar_docs)} similar documents:")
    for i, sim_doc in enumerate(similar_docs):
        print(f"\nSimilar Document {i+1}:")
        print(f"  Max similarity: {sim_doc['max_similarity']:.4f}")
        print(f"  Average similarity: {sim_doc['average_similarity']:.4f}")
        print(f"  Similar sentence pairs: {sim_doc['similar_pairs']}")
        print(f"  Document sentences: {sim_doc['document_info']['embedded_sentences']}")


def main():
    """Main function to run all examples."""
    print("Embedding Service Examples")
    print("=" * 50)
    
    try:
        # Run examples
        example_basic_embedding()
        example_document_processing()
        example_document_comparison()
        example_pdf_processing()
        example_directory_processing()
        example_plagiarism_detection()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
