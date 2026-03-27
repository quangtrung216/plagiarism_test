from __future__ import annotations

import re
from typing import List, Set

try:
    from underthesea import word_tokenize, sent_tokenize
except ImportError:
    raise ImportError(
        "Missing dependency 'underthesea'. Install it with: pip install underthesea"
    )


class TextPreprocessor:
    """Text preprocessing utilities for Vietnamese text processing."""
    
    def __init__(self, min_words: int = 8):
        """
        Initialize text preprocessor.
        
        Args:
            min_words: Minimum number of words for a sentence to be considered valid
        """
        self.min_words = min_words
        self.stopwords = self._load_vietnamese_stopwords()
    
    def _load_vietnamese_stopwords(self) -> Set[str]:
        """Load Vietnamese stopwords."""
        # Common Vietnamese stopwords
        vietnamese_stopwords = {
            "và", "là", "của", "có", "cho", "trong", "với", "để", "mà", "từ",
            "được", "thì", "khi", "nếu", "nhưng", "hoặc", "cũng", "đã", "chưa",
            "sẽ", "đang", "vẫn", "lại", "nữa", "ra", "vào", "lên", "xuống",
            "đi", "làm", "nói", "bắt", "gặp", "xem", "nghe", "biết", "tìm",
            "đến", "tới", "qua", "kia", "này", "đó", "ấy", "mình", "tôi",
            "bạn", "anh", "chị", "em", "họ", "chúng ta", "chúng tôi", "các bạn",
            "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín", "mười",
            "nhiều", "ít", "to", "nhỏ", "dài", "ngắn", "cao", "thấp", "rộng",
            "hẹp", "mới", "cũ", "tốt", "xấu", "đẹp", "đơn giản", "phức tạp",
            "nhanh", "chậm", "sớm", "muộn", "trước", "sau", "bên trên", "bên dưới",
            "ở", "tại", "về", "đối với", "theo", "bằng", "như", "giống", "khác",
            "tất cả", "mọi", "cả", "từng", "mỗi", "các", "những", "vài", "một số",
            "chỉ", "chỉ có", "duy nhất", "riêng", "khác", "khác nữa", "còn lại",
            "thực sự", "thực sự là", "quá", "rất", "hơi", "khá", "gần", "gần như",
            "hầu hết", "phần lớn", "đa số", "ít nhất", "tối đa", "trung bình",
            "tuy nhiên", "do đó", "vì vậy", "bởi vậy", "thế nên", "cho nên",
            "không", "chưa", "đừng", "hãy", "được không", "có phải không", "phải không",
            "à", "ạ", "nhỉ", "chứ", "hả", "hử", "ừ", "ừm", "à", "à mà", "à mà",
            "thôi", "thôi thì", "thôi được", "thôi nhé", "thôi nha", "thôi nào",
            "ôi", "ôi thôi", "ôi thôi thôi", "trời", "trời ơi", "trời đất ơi",
            "chao ôi", "thật sự", "quá thật", "đúng vậy", "đúng thế", "chính xác",
            "tất nhiên", "hiển nhiên", "dĩ nhiên", "tự nhiên", "nhiên nhiên"
        }
        return {word.lower() for word in vietnamese_stopwords}
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing extra whitespace and special characters.
        
        Args:
            text: Input text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        # Remove special characters but keep Vietnamese diacritics and punctuation
        text = re.sub(r'[^\w\s\.,!?;:()\-"\']', ' ', text)
        return text
    
    def tokenize_sentence(self, text: str) -> List[str]:
        """
        Tokenize text into sentences using underthesea.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        try:
            sentences = sent_tokenize(text)
            return [self.clean_text(sent) for sent in sentences if sent.strip()]
        except Exception as e:
            # Fallback to simple split if underthesea fails
            sentences = re.split(r'[.!?]+', text)
            return [self.clean_text(sent) for sent in sentences if sent.strip()]
    
    def tokenize_words(self, sentence: str) -> List[str]:
        """
        Tokenize sentence into words using underthesea.
        
        Args:
            sentence: Input sentence
            
        Returns:
            List of words
        """
        try:
            words = word_tokenize(sentence)
            return [word.lower() for word in words if word.strip()]
        except Exception as e:
            # Fallback to simple split if underthesea fails
            words = sentence.split()
            return [word.lower() for word in words if word.strip()]
    
    def remove_stopwords(self, words: List[str]) -> List[str]:
        """
        Remove stopwords from list of words.
        
        Args:
            words: List of words
            
        Returns:
            List of words without stopwords
        """
        return [word for word in words if word not in self.stopwords]
    
    def is_valid_sentence(self, sentence: str) -> bool:
        """
        Check if sentence meets minimum word count requirement.
        
        Args:
            sentence: Input sentence
            
        Returns:
            True if sentence is valid, False otherwise
        """
        words = self.tokenize_words(sentence)
        meaningful_words = [w for w in words if w not in self.stopwords]
        return len(meaningful_words) >= self.min_words
    
    def preprocess_text(self, text: str) -> List[str]:
        """
        Main preprocessing pipeline:
        1. Split text into sentences
        2. Filter sentences with minimum words
        3. Tokenize each sentence
        4. Remove stopwords
        5. Return processed sentences
        
        Args:
            text: Input text
            
        Returns:
            List of processed sentences (lowercase, stopwords removed)
        """
        # Step 1: Split into sentences
        sentences = self.tokenize_sentence(text)
        
        processed_sentences = []
        
        for sentence in sentences:
            # Step 2: Filter by minimum word count
            if not self.is_valid_sentence(sentence):
                continue
            
            # Step 3: Tokenize words
            words = self.tokenize_words(sentence)
            
            # Step 4: Remove stopwords
            filtered_words = self.remove_stopwords(words)
            
            # Step 5: Join back to sentence
            if filtered_words:  # Only add if there are words left
                processed_sentence = ' '.join(filtered_words)
                processed_sentences.append(processed_sentence)
        
        return processed_sentences
    
    def preprocess_document(self, text: str) -> dict:
        """
        Preprocess entire document and return detailed information.
        
        Args:
            text: Input document text
            
        Returns:
            Dictionary with preprocessing results
        """
        original_sentences = self.tokenize_sentence(text)
        
        processed_sentences = []
        valid_count = 0
        filtered_count = 0
        
        for sentence in original_sentences:
            words = self.tokenize_words(sentence)
            meaningful_words = [w for w in words if w not in self.stopwords]
            
            if len(meaningful_words) >= self.min_words:
                valid_count += 1
                filtered_words = self.remove_stopwords(words)
                if filtered_words:
                    processed_sentence = ' '.join(filtered_words)
                    processed_sentences.append(processed_sentence)
            else:
                filtered_count += 1
        
        return {
            'original_sentences': original_sentences,
            'processed_sentences': processed_sentences,
            'stats': {
                'total_sentences': len(original_sentences),
                'valid_sentences': valid_count,
                'filtered_sentences': filtered_count,
                'final_sentences': len(processed_sentences)
            }
        }
