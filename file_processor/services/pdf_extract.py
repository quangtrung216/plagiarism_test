import fitz  # PyMuPDF
import io
import re


def extract_pdf_text(pdf_bytes: bytes) -> str:
    text = ""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    for page in doc:
        page_text = page.get_text("text")
        page_text = page_text.replace("\n", "")  # Xóa dấu nối ở cuối dòng
        text += page_text + "\n"
    doc.close()
    return text

# def extract_pdf_blocks_with_bbox(pdf_bytes: bytes):
#     pages = []
#     doc = fitz.open(stream=pdf_bytes, filetype="pdf")
#     for page_index, page in enumerate(doc, start=1):
#         data = page.get_text("dict")
#         page_blocks = []
#         page_rect = page.rect # Lấy kích thước trang
#         for block in data["blocks"]:
#             if block["type"] != 0:  # text block
#                 continue
#             block_text = []
#             x0, y0, x1, y1 = block["bbox"]

#             for line in block["lines"]:
#                 for span in line["spans"]:
#                     block_text.append(span["text"])
            
#             # clean 
#             text = " ".join(block_text)
#             text = " ".join(text.split())  # Xóa khoảng trắng thừa
#             text = text.strip()
#             if text.isdigit():
#                 continue
#             if len(text.split()) < 5:
#                 continue
#             page_blocks.append({
#                 "text": text,
#                 "bbox": [x0, y0, x1, y1]
#                 "page_width": page_rect.width,
#                 "page_height": page_rect.height
#             })

#         pages.append({
#             "page": page_index,
#             "blocks": page_blocks
#         })

#     doc.close()
#     return pages

def extract_pdf_blocks_with_bbox(pdf_bytes: bytes):
    pages = []
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    for page_index, page in enumerate(doc, start=1):
        data = page.get_text("dict")
        page_blocks = []
        page_rect = page.rect  # thêm metadata 
        for block in data["blocks"]:
            if block["type"] != 0:
                continue
            block_text = []
            x0, y0, x1, y1 = block["bbox"]

            for line in block["lines"]:
                for span in line["spans"]:
                    block_text.append(span["text"])
            text = " ".join(block_text)
            text = " ".join(text.split())   # collapse spaces
            text = text.strip()

            if not text:
                continue
            if text.isdigit():
                continue

            if len(text.split()) < 5:
                continue

            page_blocks.append({
                "text": text,
                "bbox": [x0, y0, x1, y1],
                "page_width": page_rect.width,
                "page_height": page_rect.height
            })

        pages.append({
            "page": page_index,
            "blocks": page_blocks
        })

    doc.close()
    return pages
