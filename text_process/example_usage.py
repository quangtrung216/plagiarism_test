#!/usr/bin/env python3
"""
Example usage of text processing utilities for PDF documents
"""

from pathlib import Path
from text_process import TextPreprocessor, PDFProcessor


def example_text_preprocessing():
    """Example of text preprocessing."""
    print("=== Text Preprocessing Example ===")
    
    # Sample Vietnamese text
    sample_text = """
    Đây là một câu ví dụ để kiểm tra hệ thống xử lý văn bản. 
    Hệ thống này có thể tách văn bản thành các câu và xử lý từng câu một.
    Các câu quá ngắn sẽ bị loại bỏ. Đây là một câu đủ dài để được giữ lại.
    Chào bạn.
    Trí tuệ nhân tạo đang phát triển rất nhanh trong những năm gần đây.
    """
    
    # Initialize preprocessor with minimum 8 words per sentence
    preprocessor = TextPreprocessor(min_words=8)
    
    # Preprocess text
    result = preprocessor.preprocess_document(sample_text)
    
    print(f"Original sentences: {len(result['original_sentences'])}")
    print(f"Valid sentences: {result['stats']['valid_sentences']}")
    print(f"Final processed sentences: {len(result['processed_sentences'])}")
    
    print("\nOriginal sentences:")
    for i, sent in enumerate(result['original_sentences']):
        print(f"{i+1}. {sent}")
    
    print("\nProcessed sentences:")
    for i, sent in enumerate(result['processed_sentences']):
        print(f"{i+1}. {sent}")


def example_pdf_processing():
    """Example of PDF processing."""
    print("\n=== PDF Processing Example ===")
    
    # Initialize PDF processor
    processor = PDFProcessor(min_words=8)
    
    # Example usage with a PDF file (you need to provide actual PDF path)
    pdf_path = "sample.pdf"  # Replace with actual PDF path
    
    if Path(pdf_path).exists():
        try:
            # Process single PDF
            result = processor.process_pdf(pdf_path)
            
            print(f"Processed: {result['pdf_info']['file_name']}")
            print(f"File size: {result['pdf_info']['file_size']} bytes")
            print(f"Total sentences: {result['stats']['total_sentences']}")
            print(f"Valid sentences: {result['stats']['valid_sentences']}")
            print(f"Final sentences: {result['stats']['final_sentences']}")
            
            # Get sentences with metadata
            sentences_with_meta = processor.extract_sentences_with_metadata(pdf_path)
            print(f"\nFirst 5 processed sentences:")
            for i, sent_info in enumerate(sentences_with_meta[:5]):
                print(f"{i+1}. [{sent_info['word_count']} words] {sent_info['sentence']}")
                
        except Exception as e:
            print(f"Error processing PDF: {e}")
    else:
        print(f"PDF file not found: {pdf_path}")
        print("Please replace 'sample.pdf' with an actual PDF file path")


def example_directory_processing():
    """Example of processing multiple PDFs in a directory."""
    print("\n=== Directory Processing Example ===")
    
    processor = PDFProcessor(min_words=8)
    
    # Example usage with a directory containing PDFs
    pdf_directory = "./pdfs"  # Replace with actual directory path
    
    if Path(pdf_directory).exists():
        try:
            results = processor.process_directory(pdf_directory, recursive=True)
            
            total_sentences = 0
            total_files = len(results)
            
            for result in results:
                if 'error' not in result['pdf_info']:
                    total_sentences += result['stats']['final_sentences']
                    print(f"✓ {result['pdf_info']['file_name']}: {result['stats']['final_sentences']} sentences")
                else:
                    print(f"✗ {result['pdf_info']['file_name']}: {result['pdf_info']['error']}")
            
            print(f"\nProcessed {total_files} files")
            print(f"Total extracted sentences: {total_sentences}")
            
        except Exception as e:
            print(f"Error processing directory: {e}")
    else:
        print(f"Directory not found: {pdf_directory}")
        print("Please replace './pdfs' with an actual directory path")


def main():
    """Main function to run all examples."""
    example_text_preprocessing()
    example_pdf_processing()
    example_directory_processing()


if __name__ == "__main__":
    main()
