"""
Standalone test script để extract sentences từ PDF và DOCX files
Không cần chạy FastAPI server
"""
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.file_process_service import FileProcessService
from nlp.text_preprocess import (
    preprocess_pdf_text,
    normalize_full_text,
    extract_plagiarism_zone,
    extract_valid_sentences
)


def print_header(title: str):
    """In tiêu đề"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def test_extract_sentences_from_file(
    file_path: str,
    min_words: int = 8,
    max_words: int = 200,
    language: str = "vi",
    use_zone: bool = True
) -> Dict[str, Any]:
    """
    Extract sentences từ PDF hoặc DOCX file
    """
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"❌ File không tồn tại: {file_path}")
        return None
    
    file_extension = file_path.suffix.lower()
    
    if file_extension not in [".pdf", ".docx"]:
        print(f"❌ File type không hỗ trợ: {file_extension}")
        return None
    
    print(f"\n📄 Đang xử lý: {file_path.name}")
    print(f"📊 Tham số: min_words={min_words}, max_words={max_words}, language={language}, use_zone={use_zone}")
    
    try:
        # Extract text
        if file_extension == ".pdf":
            result = FileProcessService.extract_text_from_pdf(str(file_path))
        else:  # .docx
            result = FileProcessService.extract_text_from_word(str(file_path))
        
        if not result.get("success"):
            print(f"❌ Lỗi: {result.get('error')}")
            return None
        
        raw_text = result.get("text", "")
        print(f"✅ Extract text thành công ({len(raw_text)} ký tự)")
        
        # Preprocess sentences
        sentences = preprocess_pdf_text(
            raw_text=raw_text,
            language=language,
            min_words=min_words,
            max_words=max_words,
            use_zone=use_zone
        )
        
        print(f"✅ Extract {len(sentences)} câu hợp lệ")
        
        return {
            "file_name": file_path.name,
            "file_type": file_extension,
            "total_sentences": len(sentences),
            "sentences": sentences,
            "raw_text_length": len(raw_text),
            "metadata": result
        }
        
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def display_results(result: Dict[str, Any]):
    """Hiển thị kết quả"""
    
    if not result:
        return
    
    print(f"\n📋 Kết quả cho file: {result['file_name']}")
    print(f"   - Tổng câu: {result['total_sentences']}")
    print(f"   - Độ dài text gốc: {result['raw_text_length']} ký tự")
    
    print(f"\n📝 Các câu được extract (hiển thị 10 câu đầu):")
    print("-" * 70)
    
    for i, sentence in enumerate(result['sentences'][:10], 1):
        print(f"{i}. {sentence[:100]}..." if len(sentence) > 100 else f"{i}. {sentence}")
    
    if result['total_sentences'] > 10:
        print(f"\n... và {result['total_sentences'] - 10} câu khác")


def test_extract_text_only(file_path: str):
    """Extract chỉ text (không tiền xử lý)"""
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"❌ File không tồn tại: {file_path}")
        return
    
    file_extension = file_path.suffix.lower()
    
    if file_extension not in [".pdf", ".docx"]:
        print(f"❌ File type không hỗ trợ: {file_extension}")
        return
    
    print(f"\n📄 Extract text từ: {file_path.name}")
    
    try:
        if file_extension == ".pdf":
            result = FileProcessService.extract_text_from_pdf(str(file_path))
        else:
            result = FileProcessService.extract_text_from_word(str(file_path))
        
        if not result.get("success"):
            print(f"❌ Lỗi: {result.get('error')}")
            return
        
        text = result.get("text", "")
        print(f"✅ Extract text thành công ({len(text)} ký tự)")
        print(f"\n📝 Text content (first 500 chars):")
        print("-" * 70)
        print(text[:500])
        if len(text) > 500:
            print("\n... (tiếp tục) ...")
        
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")


def test_extract_plagiarism_zone(file_path: str):
    """Extract plagiarism zone"""
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"❌ File không tồn tại: {file_path}")
        return
    
    file_extension = file_path.suffix.lower()
    
    if file_extension not in [".pdf", ".docx"]:
        print(f"❌ File type không hỗ trợ: {file_extension}")
        return
    
    print(f"\n📄 Extract plagiarism zone từ: {file_path.name}")
    
    try:
        if file_extension == ".pdf":
            result = FileProcessService.extract_text_from_pdf(str(file_path))
        else:
            result = FileProcessService.extract_text_from_word(str(file_path))
        
        if not result.get("success"):
            print(f"❌ Lỗi: {result.get('error')}")
            return
        
        raw_text = result.get("text", "")
        normalized_text = normalize_full_text(raw_text)
        plagiarism_zone = extract_plagiarism_zone(normalized_text)
        
        print(f"✅ Extract plagiarism zone thành công")
        print(f"   - Original text: {len(raw_text)} ký tự")
        print(f"   - Plagiarism zone: {len(plagiarism_zone)} ký tự")
        print(f"\n📝 Plagiarism zone content (first 500 chars):")
        print("-" * 70)
        print(plagiarism_zone[:500])
        if len(plagiarism_zone) > 500:
            print("\n... (tiếp tục) ...")
        
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")


def main():
    """Main test function"""
    
    print_header("TEST EXTRACT SENTENCES - File Processor")
    print("\n📌 Hướng dẫn sử dụng:")
    print("   1. Chạy script này với đường dẫn file PDF hoặc DOCX")
    print("   2. Script sẽ extract text và tách câu từ file")
    print("   3. Kết quả sẽ được hiển thị trên console")
    
    # Test files
    test_files = [
        "uploads/test_document.txt",  # Nếu có
        "../backend/uploads/test_document.txt",
    ]
    
    # Tìm file test
    test_file = None
    for potential_path in test_files:
        if Path(potential_path).exists():
            test_file = potential_path
            break
    
    if not test_file:
        print("\n⚠️  Không tìm thấy file test mặc định")
        print("   Vui lòng sử dụng hàm test_extract_sentences_from_file() hoặc")
        print("   chạy script với tham số file path")
        print("\n📝 Ví dụ sử dụng trong code:")
        print("   from test_extract_sentences_standalone import test_extract_sentences_from_file")
        print("   result = test_extract_sentences_from_file('path/to/file.pdf')")
        print("   display_results(result)")
        return
    
    print(f"\n✅ Tìm thấy file test: {test_file}")
    
    # Test extract sentences
    print_header("TEST 1: Extract Sentences")
    result = test_extract_sentences_from_file(test_file)
    display_results(result)
    
    # Test extract text only
    print_header("TEST 2: Extract Text Only")
    test_extract_text_only(test_file)
    
    # Test extract plagiarism zone
    print_header("TEST 3: Extract Plagiarism Zone")
    test_extract_plagiarism_zone(test_file)
    
    print_header("Test Hoàn Thành")


if __name__ == "__main__":
    main()
