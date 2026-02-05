import fitz  # PyMuPDF
import io


def extract_pdf_text(pdf_bytes: bytes) -> str:
    """
    Convert PDF bytes to raw text
    """

    text = ""

    doc = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    for page in doc:
        page_text = page.get_text("text")
        text += page_text + "\n"

    doc.close()

    return text

def extract_pdf_blocks_with_bbox(pdf_bytes: bytes):
    """
    Extract text blocks with page number and bbox
    """

    pages = []

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    for page_index, page in enumerate(doc, start=1):

        data = page.get_text("dict")

        page_blocks = []

        for block in data["blocks"]:
            if block["type"] != 0:  # text block
                continue
            block_text = []
            x0, y0, x1, y1 = block["bbox"]

            for line in block["lines"]:
                for span in line["spans"]:
                    block_text.append(span["text"])
            text = " ".join(block_text).strip()
            if not text:
                continue

            page_blocks.append({
                "text": text,
                "bbox": [x0, y0, x1, y1]
            })

        pages.append({
            "page": page_index,
            "blocks": page_blocks
        })

    doc.close()

    return pages
