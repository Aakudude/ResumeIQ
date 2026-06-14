import pdfplumber
import re
from pathlib import Path
from typing import Optional


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file using pdfplumber."""
    try:
        text_parts = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        return "\n".join(text_parts)
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")


def extract_text_from_string(content: str) -> str:
    """Clean and normalize text content."""
    # Remove excessive whitespace
    content = re.sub(r'\n{3,}', '\n\n', content)
    content = re.sub(r' {2,}', ' ', content)
    return content.strip()


def validate_pdf(file_path: str) -> bool:
    """Validate that file is a readable PDF."""
    try:
        with pdfplumber.open(file_path) as pdf:
            return len(pdf.pages) > 0
    except Exception:
        return False
