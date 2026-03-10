"""Resume parser: extract structured data from PDF resumes via PyMuPDF."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """Extract raw text from a PDF file using PyMuPDF.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Extracted text as a single string.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
        ImportError: If PyMuPDF is not installed.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"Resume PDF not found: {pdf_path}")

    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise ImportError(
            "PyMuPDF is required for PDF parsing. "
            "Install via: pip install pymupdf"
        )

    doc = fitz.open(str(pdf_path))
    text_parts: list[str] = []
    for page in doc:
        text_parts.append(page.get_text())
    doc.close()

    return "\n".join(text_parts)


def save_text(text: str, output_path: str | Path) -> Path:
    """Save extracted text to a file.

    Args:
        text: Text content to save.
        output_path: Path for the output text file.

    Returns:
        Path to the saved file.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")
    return output_path


def parse_resume(pdf_path: str | Path, output_path: str | Path | None = None) -> dict[str, Any]:
    """Parse a resume PDF and return structured data.

    Args:
        pdf_path: Path to the resume PDF.
        output_path: Optional path to save extracted text.

    Returns:
        Dict with keys: raw_text, source_path, char_count, line_count.
    """
    text = extract_text_from_pdf(pdf_path)

    if output_path:
        save_text(text, output_path)

    return {
        "raw_text": text,
        "source_path": str(pdf_path),
        "char_count": len(text),
        "line_count": text.count("\n") + 1,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python resume_parser.py <pdf_path> [output_path]")
        sys.exit(1)

    pdf = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    result = parse_resume(pdf, out)
    print(f"Parsed: {result['source_path']}")
    print(f"  Characters: {result['char_count']}")
    print(f"  Lines: {result['line_count']}")
    if out:
        print(f"  Saved to: {out}")
