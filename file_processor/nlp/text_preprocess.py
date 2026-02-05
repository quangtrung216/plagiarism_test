import re
import unicodedata
from typing import List
import nltk
from nltk.tokenize import sent_tokenize
from underthesea import sent_tokenize as vi_sent_tokenize
import os 

# STOPWORDS = {
#     "là", "và", "thì", "được", "của", "với", "cho", "trong",
#     "khi", "một", "các", "những", "đã", "đang", "sẽ", "này", "đó"
# }

# def normalize_text(text: str) -> str:
#     text = unicodedata.normalize("NFC", text)
#     text = text.lower()
#     text = re.sub(r"[\r\n\t]+", " ", text)
#     text = re.sub(r"[^a-zA-Z0-9àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđĐ\s]", " ", text)
#     return text

def is_toc_line(text: str) -> bool:

    text = text.lower().strip()

    # Có chữ "mục lục"
    if "mục lục" in text:
        return True

    # Dạng: chương 1 ..... 3
    if re.search(r"\.{3,}\s*\d+$", text):
        return True

    # Dạng: title + số trang
    if re.search(r"\s+\d+$", text) and len(text.split()) < 8:
        return True

    return False

# Load stopwords from file
def load_stopwords(file_path: str) -> set:
    stopwords = set()
    if not os.path.exists(file_path):
        print(f"[WARN] Stopwords file not found: {file_path}")
        return stopwords
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            word = line.strip().lower()
            if word:
                stopwords.add(word)
    return stopwords

# Remove stopwords from text
def remove_stopword(text: str, stopwords: set) -> str:
    if not text:
        return ""
    words = text.split()
    filtered_words = [word for word in words if word not in stopwords]
    return " ".join(filtered_words)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STOPWORDS_FILE = os.path.join(BASE_DIR, "../data/vietnamese-stopwords.txt")
VI_STOPWORDS = load_stopwords(STOPWORDS_FILE)

IGNORE_SECTIONS = [
    "BÌA",
    "NHẬN XÉT",
    "LỜI CAM ĐOAN",
    "LỜI CẢM ƠN",
    "MỤC LỤC",
    "DANH MỤC",
]



# Viết thường cho các kí tự
def normalize_text_lowercase(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    text = text.lower()
    return text


# Xoá xuống dòng
def normalize_lines(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
    text = re.sub(r'\n{2,}', '\n\n', text)
    return text.strip()

# Tách câu hợp lệ
def extract_valid_sentences(text: str, min_words: int = 8, language: str = "vi") -> List[str]:
    if not text:
        return []
    text = unicodedata.normalize("NFC", text)
    text = text.lower()
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
    text = re.sub(r'\n{2,}', '\n\n', text)
    # Tách đoạn 
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    valid_sentences = []
    # Tách câu trong từng đoạn
    for para in paragraphs:
        if language == "vi":
            sentences = vi_sent_tokenize(para)
        else:
            sentences = sent_tokenize(para)
        for sentence in sentences:
            if len(sentence.strip().split()) >= min_words:
                valid_sentences.append(sentence.strip())
    return valid_sentences

# Hàm trích xuất nội dung chính từ văn bản PDF

def extract_academic_content(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    # tìm điểm kết thúc của tài liệu
    end_pattenrs = re.compile(r'^\s*(KẾT\s+LUẬN|TÀI\s+LIỆU\s+THAM\s+KHẢO|PHỤ\s+LỤC|REFERENCES|APPENDIX|BIBLIOGRAPHY)', re.IGNORECASE | re.MULTILINE)
    end_match = end_pattenrs.search(text)
    end_idx = end_match.start() if end_match else len(text)
    main_text = text[:end_idx]
    # Tìm chương đầu tiên
    chapter_patterns = re.compile(r'^\s*(CHƯƠNG|Chapter)\s+(\d+|[IVX]+)', re.IGNORECASE | re.MULTILINE)
    first_chapter = chapter_patterns.search(main_text)
    if not first_chapter:
        return ""
    return main_text[first_chapter.start():].strip()


# Luồng
def preprocess_pdf_text(raw_text: str, language: str = "vi", min_words: int = 8, max_words: int = 200) -> str:
    if not raw_text:
        return []
    academic_text = extract_academic_content(raw_text)
    if not academic_text:
        return []
    academic_text = normalize_text_lowercase(academic_text)
    academic_text = normalize_lines(academic_text)
    sentences = extract_valid_sentences(academic_text, min_words=min_words, language=language)
    clean_sentences = []
    for sentence in sentences:
        s_clean = remove_stopword(sentence, VI_STOPWORDS)
        if s_clean.strip():
            clean_sentences.append(s_clean)
    return clean_sentences




# def main():
#     # ===== TEST TEXT (có thể thay bằng text đọc từ PDF) =====
#     raw_text = """
#     BÌA BÁO CÁO

#     LỜI CAM ĐOAN
#     Tôi xin cam đoan đây là công trình nghiên cứu của riêng tôi.

#     CHƯƠNG 1 TỔNG QUAN
#     Học máy là một lĩnh vực quan trọng của trí tuệ nhân tạo.
#     Nó cho phép máy tính học từ dữ liệu và đưa ra dự đoán chính xác.
#     Các phương pháp học máy ngày càng được áp dụng rộng rãi trong thực tế.

#     CHƯƠNG 2 PHƯƠNG PHÁP NGHIÊN CỨU
#     Dữ liệu được thu thập từ nhiều nguồn khác nhau.
#     Mô hình được huấn luyện và đánh giá bằng các chỉ số tiêu chuẩn.

#     KẾT LUẬN
#     Báo cáo đã trình bày các nội dung chính của đề tài.
#     """

#     # ===== CHẠY PIPELINE =====
#     sentences = preprocess_pdf_text(
#         raw_text=raw_text,
#         language="vi",
#         min_words=8
#     )

#     # ===== IN KẾT QUẢ =====
#     print("===== KẾT QUẢ TIỀN XỬ LÍ =====")
#     print(f"Tổng số câu hợp lệ: {len(sentences)}\n")

#     for i, s in enumerate(sentences[:10], 1):
#         print(f"{i}. {s}")


# if __name__ == "__main__":
#     main()