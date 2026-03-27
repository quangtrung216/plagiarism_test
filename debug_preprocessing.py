"""
Debug Vietnamese text preprocessing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from text_process.preprocessor import TextPreprocessor

def debug_preprocessing():
    """Debug Vietnamese text preprocessing"""
    
    print("🔍 Debug Vietnamese Text Preprocessing")
    print("=" * 50)
    
    # Test sentences
    test_sentences = [
        "Đây là một câu test để kiểm tra MinHash và embedding.",
        "Machine learning là một nhánh của trí tuệ nhân tạo.",
        "Học máy giúp máy tính học từ dữ liệu.",
        "AI đang thay đổi thế giới.",
        "Trí tuệ nhân tạo rất quan trọng."
    ]
    
    preprocessor = TextPreprocessor(min_words=3)
    
    print(f"📊 Min words threshold: {preprocessor.min_words}")
    print(f"📝 Stopwords count: {len(preprocessor.stopwords)}")
    print()
    
    for i, sentence in enumerate(test_sentences, 1):
        print(f"🔍 Test {i}: {sentence}")
        
        # Tokenize
        words = preprocessor.tokenize_words(sentence)
        print(f"   📝 Words: {words}")
        
        # Remove stopwords
        filtered_words = preprocessor.remove_stopwords(words)
        print(f"   🗑️  Filtered: {filtered_words}")
        
        # Check validity
        is_valid = preprocessor.is_valid_sentence(sentence)
        print(f"   ✅ Valid: {is_valid} (needs {preprocessor.min_words}+ meaningful words)")
        
        # Preprocess
        processed = preprocessor.preprocess_text(sentence)
        print(f"   🔧 Processed: {processed}")
        
        print()
    
    # Test document processing
    test_text = "Đây là một câu test để kiểm tra MinHash và embedding. Machine learning là một nhánh của trí tuệ nhân tạo."
    
    print("📄 Document Processing Test:")
    print(f"📝 Input: {test_text}")
    
    result = preprocessor.preprocess_document(test_text)
    
    print(f"📊 Results:")
    print(f"   - Original sentences: {result['original_sentences']}")
    print(f"   - Processed sentences: {result['processed_sentences']}")
    print(f"   - Stats: {result['stats']}")

if __name__ == "__main__":
    debug_preprocessing()
