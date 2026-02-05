import sys
import os 

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)
from nlp.text_preprocess import preprocess_pdf_text

def main():
    raw_text = """
    BÌA

    ĐỒ ÁN TỐT NGHIỆP

    CHƯƠNG 1: GIỚI THIỆU

    Học máy là một lĩnh vực của trí tuệ nhân tạo
    cho phép hệ thống học từ dữ liệu và cải thiện
    hiệu suất theo thời gian.

    LỜI CẢM ƠN

    Em xin cảm ơn thầy cô...
    """

    print("========== INPUT ==========")
    print(raw_text)

    print("\n========== OUTPUT ==========")

    results = preprocess_pdf_text(raw_text)

    for i, s in enumerate(results, 1):
        print(f"{i}. {s}")

if __name__ == "__main__":
    main()