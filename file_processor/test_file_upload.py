"""
Test script for the preprocess file upload API.

Usage:
    python test_file_upload.py <file_path> [--language vi] [--min-words 8]
        [--max-words 200] [--no-zone]
"""

import argparse
import json
from pathlib import Path

import requests


API_URL = "http://localhost:8001/api/preprocess/upload"
SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


def test_file_upload(
    file_path: str,
    language: str = "vi",
    min_words: int = 8,
    max_words: int = 200,
    use_zone: bool = True,
) -> None:
    """Upload a file to the preprocess endpoint and print a small summary."""

    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        return

    file_ext = path.suffix.lower()
    if file_ext not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        print(f"Unsupported file type: {file_ext}")
        print(f"Supported: {supported}")
        return

    print(f"Uploading file: {file_path}")
    print(
        "Settings:",
        json.dumps(
            {
                "language": language,
                "min_words": min_words,
                "max_words": max_words,
                "use_zone": use_zone,
            },
            ensure_ascii=False,
        ),
    )

    try:
        with path.open("rb") as f:
            files = {"file": (path.name, f)}
            params = {
                "language": language,
                "min_words": min_words,
                "max_words": max_words,
                "use_zone": use_zone,
            }
            response = requests.post(API_URL, files=files, params=params, timeout=60)

        if response.status_code != 200:
            print(f"Error {response.status_code}: {response.text}")
            return

        result = response.json()
        print("Success")
        print(f"File type: {result.get('file_type')}")
        print(f"Total sentences extracted: {result.get('total_sentences')}")
        print(
            "Metadata:",
            json.dumps(result.get("metadata", {}), indent=2, ensure_ascii=False),
        )

        sentences = result.get("sentences", [])
        if sentences:
            print("First 5 sentences:")
            for idx, sentence in enumerate(sentences[:5], start=1):
                preview = sentence[:120]
                suffix = "..." if len(sentence) > 120 else ""
                print(f"{idx}. {preview}{suffix}")

        output_file = path.with_name(f"{path.stem}_extracted.json")
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"Saved response to: {output_file}")

    except requests.exceptions.ConnectionError:
        print(f"Connection error. Make sure the API server is running at {API_URL}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test preprocess file upload API")
    parser.add_argument("file", help="Path to a PDF or DOCX file")
    parser.add_argument("--language", default="vi", help="Language: vi or en")
    parser.add_argument(
        "--min-words", type=int, default=8, help="Minimum words per sentence"
    )
    parser.add_argument(
        "--max-words", type=int, default=200, help="Maximum words per sentence"
    )
    parser.add_argument(
        "--no-zone", action="store_true", help="Disable plagiarism-zone extraction"
    )

    args = parser.parse_args()
    test_file_upload(
        args.file,
        language=args.language,
        min_words=args.min_words,
        max_words=args.max_words,
        use_zone=not args.no_zone,
    )
