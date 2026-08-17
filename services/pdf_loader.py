import os
from pathlib import Path
from pypdf import PdfReader


def load_pdf_text(pdf_path: str) -> list[dict]:
    """Extract text per page from a PDF. Returns [{"text": ..., "page": ...}]."""
    reader = PdfReader(pdf_path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            pages.append({"text": text, "page": i + 1})
    return pages


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """Split text into overlapping chunks by character count."""
    chunks = []
    start = 0
    length = len(text)
    while start < length:
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def load_and_chunk_directory(data_dir: str) -> list[dict]:
    """
    Walk a directory of PDFs, extract + chunk text.
    Returns list of {"text": ..., "source": filename, "page": page_num}.
    """
    results = []
    data_path = Path(data_dir)

    for pdf_file in sorted(data_path.glob("*.pdf")):
        pages = load_pdf_text(str(pdf_file))
        for page_data in pages:
            chunks = chunk_text(page_data["text"])
            for chunk in chunks:
                results.append({
                    "text": chunk,
                    "source": pdf_file.name,
                    "page": page_data["page"],
                })

    return results