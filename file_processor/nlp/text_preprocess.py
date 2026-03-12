import re
import unicodedata
from typing import List
import nltk
from nltk.tokenize import sent_tokenize
from underthesea import sent_tokenize as vi_sent_tokenize
import os 
import fitz

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

IGNORE_START = [
    "LỜI CAM ĐOAN",
    "LỜI CẢM ƠN",
    "MỤC LỤC",
    "DANH MỤC"
]

START_CONTENT = [
    r"CHƯƠNG\s+1",
    r"CHƯƠNG\s+I",
    r"PHẦN\s+1",
    r"GIỚI\s+THIỆU"
]

STOP_CONTENT = [
    "TÀI LIỆU THAM KHẢO",
    "REFERENCES",
    "PHỤ LỤC"
]

def normalize_full_text(text: str) -> str:
    if not text:
        return ""

    text = unicodedata.normalize("NFC", text)

    # Chuẩn newline
    text = re.sub(r'\r\n?', '\n', text)

    # Bỏ multiple spaces
    text = re.sub(r'[ \t]+', ' ', text)

    # Bỏ ký tự trang
    text = text.replace("\f", " ")

    return text.strip()

def normalize_full_text(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    # Chuẩn newline
    text = re.sub(r'\r\n?', '\n', text)
    # Bỏ multiple spaces
    text = re.sub(r'[ \t]+', ' ', text)
    # Bỏ ký tự trang
    text = text.replace("\f", " ")
    return text.strip()

def extract_plagiarism_zone(text: str) -> str:
    lines = text.split("\n")

    start_idx = None
    stop_idx = None

    for i, line in enumerate(lines):
        upper_line = line.strip().upper()

        # Tìm điểm bắt đầu
        if start_idx is None:
            for pattern in START_CONTENT:
                if re.search(pattern, upper_line):
                    start_idx = i
                    break

        # Tìm điểm dừng
        if any(keyword in upper_line for keyword in STOP_CONTENT):
            stop_idx = i
            break

    if start_idx is None:
        # Nếu không tìm thấy chương → fallback lấy toàn bộ
        start_idx = 0

    if stop_idx is None:
        stop_idx = len(lines)

    return "\n".join(lines[start_idx:stop_idx])


def has_valid_citation(sentence: str) -> bool:
    # (Nguyễn Văn A, 2020)
    if re.search(r'\([A-Za-zÀ-ỹ\s]+,\s*\d{4}\)', sentence):
        return True

    # [1]
    if re.search(r'\[\d+\]', sentence):
        return True

    return False


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

# xử lí trích dẫn
def is_citation_sentence(text: str) -> bool:
    text = text.strip()
    # Có dấu ngoặc kép
    if re.search(r'“.*?”|".*?"', text):
        return True
    # (Author, 2020)
    if re.search(r'\([A-Za-zÀ-ỹ\s]+,\s*\d{4}\)', text):
        return True
    if re.search(r'\[\d+\]', text):
        return True

    return False

# Luồng
def preprocess_pdf_text(raw_text: str, language: str = "vi", min_words: int = 8, max_words: int = 200, use_zone: bool = True) -> str:
    if not raw_text:
        return []
     # ===== BƯỚC 1: Chuẩn hóa =====
    text = normalize_full_text(raw_text)

    # ===== BƯỚC 2: Cắt vùng tính đạo văn =====
    plagiarism_zone = extract_plagiarism_zone(text) if use_zone else text

    if not plagiarism_zone.strip():
        return []

    # ===== BƯỚC 3: Tách câu =====
    sentences = vi_sent_tokenize(plagiarism_zone)

    clean_sentences = []

    for sentence in sentences:
        sentence = sentence.strip()

        if not sentence:
            continue

        word_count = len(sentence.split())

        # Điều kiện >= 8 từ
        if word_count < min_words or word_count > max_words:
            continue

        # Nếu có trích dẫn hợp lệ → bỏ qua
        if has_valid_citation(sentence):
            continue

        clean_sentences.append(sentence.lower())

    if clean_sentences:
        return clean_sentences

    # Fallback: khi xử lý theo block nhỏ (ít dấu câu / ít từ) thì filter mặc định có thể loại hết.
    # Nới điều kiện để không trả về rỗng quá thường xuyên.
    relaxed_min_words = min(5, min_words)
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        word_count = len(sentence.split())
        if word_count < relaxed_min_words or word_count > max_words:
            continue
        clean_sentences.append(sentence.lower())

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


