import re
import unicodedata
from typing import List

from nltk.tokenize import sent_tokenize
from underthesea import sent_tokenize as vi_sent_tokenize


START_CONTENT_PATTERNS = [
    r"^\s*CHUONG\s+(?:1|I)\b",
    r"^\s*PHAN\s+(?:1|I)\b",
    r"^\s*CHAPTER\s+(?:1|I)\b",
    r"^\s*1(?:\.\d+)*\s+[^\d].*",
]

STOP_CONTENT_PATTERNS = [
    r"^\s*KET\s+LUAN\b",
    r"^\s*KET\s+LUAN\b",
    r"^\s*TAI\s+LIEU\s+THAM\s+KHAO\b",
    r"^\s*TAI\s+LIEU\s+THAM\s+KHAO\b",
    r"^\s*REFERENCES\b",
    r"^\s*BIBLIOGRAPHY\b",
    r"^\s*PHU\s+LUC\b",
    r"^\s*PHU\s+LUC\b",
    r"^\s*APPENDIX\b",
]

SKIP_LINE_PATTERNS = [
    r"^\s*LOI\s+CAM\s+ON\b",
    r"^\s*LOI\s+CAM\s+DOAN\b",
    r"^\s*MUC\s+LUC(?:\s+\w+)?\b",
    r"^\s*BANG\s+DANH\s+TU\s+VIET\s+TAT\b",
    r"^\s*NHAN\s+XET\b",
    r"^\s*GIANG\s+VIEN\b",
    r"^\s*DANH\s+MUC\b",
    r"^\s*Shortcut\s+word\b",
    r"^\s*Full\s+word\b",
    r"^\s*Description\b",
    r"^\s*(?:HINH|PICTURE|BANG|TABLE)\s+\d",
    r"^\s*•\s+",
]

TOC_LINE_PATTERNS = [
    r"^\s*CHUONG\s+\d+.*\d+\s*$",
    r"^\s*CHUONG\s+[IVX]+.*\d+\s*$",
    r"^\s*\d+(?:\.\d+)+\s*.+\d+\s*$",
]


def normalize_full_text(text: str) -> str:
    if not text:
        return ""

    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"\r\n?", "\n", text)
    text = text.replace("\f", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def _normalize_for_matching(text: str) -> str:
    text = normalize_full_text(text)
    text = _strip_accents(text)
    return text.upper()


def _matches_any(patterns: List[str], text: str) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def is_noise_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True

    comparable = _normalize_for_matching(stripped)

    if _matches_any(SKIP_LINE_PATTERNS, comparable):
        return True

    if _matches_any(TOC_LINE_PATTERNS, comparable):
        return True

    if re.fullmatch(r"[.\-_–—·•\s\d]+", stripped):
        return True

    return False


def extract_plagiarism_zone(text: str) -> str:
    lines = [line.strip() for line in normalize_full_text(text).split("\n")]

    start_idx = None
    stop_idx = len(lines)

    for idx, line in enumerate(lines):
        comparable = _normalize_for_matching(line)
        if (
            start_idx is None
            and _matches_any(START_CONTENT_PATTERNS, comparable)
            and not is_noise_line(line)
        ):
            start_idx = idx
            break

    if start_idx is None:
        return ""

    for idx in range(start_idx, len(lines)):
        comparable = _normalize_for_matching(lines[idx])
        if _matches_any(STOP_CONTENT_PATTERNS, comparable):
            stop_idx = idx
            break

    content_lines = []
    for line in lines[start_idx:stop_idx]:
        if is_noise_line(line):
            continue
        content_lines.append(line)

    return "\n".join(content_lines).strip()


def has_valid_citation(sentence: str) -> bool:
    if re.search(r"\([A-Za-zÀ-ỹ\s]+,\s*\d{4}\)", sentence):
        return True

    if re.search(r"\[\d+\]", sentence):
        return True

    return False


def normalize_lines(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    text = re.sub(r"\n{2,}", "\n\n", text)
    return text.strip()


def extract_valid_sentences(
    text: str, min_words: int = 8, language: str = "vi"
) -> List[str]:
    if not text:
        return []

    text = normalize_full_text(text)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    valid_sentences = []

    for para in paragraphs:
        sentences = vi_sent_tokenize(para) if language == "vi" else sent_tokenize(para)
        for sentence in sentences:
            cleaned = sentence.strip()
            if len(cleaned.split()) >= min_words:
                valid_sentences.append(cleaned)

    return valid_sentences


def extract_academic_content(text: str) -> str:
    return extract_plagiarism_zone(text)


def is_citation_sentence(text: str) -> bool:
    text = text.strip()
    if re.search(r"“.*?”|\".*?\"", text):
        return True
    if re.search(r"\([A-Za-zÀ-ỹ\s]+,\s*\d{4}\)", text):
        return True
    if re.search(r"\[\d+\]", text):
        return True
    return False


def preprocess_pdf_text(
    raw_text: str,
    language: str = "vi",
    min_words: int = 8,
    max_words: int = 200,
    use_zone: bool = True,
) -> List[str]:
    if not raw_text:
        return []

    text = normalize_full_text(raw_text)
    plagiarism_zone = extract_plagiarism_zone(text) if use_zone else text

    if not plagiarism_zone.strip():
        return []

    paragraphs = [p.strip() for p in plagiarism_zone.split("\n") if p.strip()]
    clean_sentences = []

    for para in paragraphs:
        if is_noise_line(para):
            continue

        sentences = vi_sent_tokenize(para) if language == "vi" else sent_tokenize(para)
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if is_noise_line(sentence):
                continue

            word_count = len(sentence.split())
            if word_count < min_words or word_count > max_words:
                continue

            if has_valid_citation(sentence):
                continue

            clean_sentences.append(sentence.lower())

    if clean_sentences:
        return clean_sentences

    relaxed_min_words = min(5, min_words)
    for para in paragraphs:
        if is_noise_line(para):
            continue

        sentences = vi_sent_tokenize(para) if language == "vi" else sent_tokenize(para)
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or is_noise_line(sentence):
                continue

            word_count = len(sentence.split())
            if word_count < relaxed_min_words or word_count > max_words:
                continue

            if has_valid_citation(sentence):
                continue

            clean_sentences.append(sentence.lower())

    return clean_sentences
