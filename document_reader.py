from pathlib import Path
from pypdf import PdfReader


def read_pdf(file_path):
    """Extract text from a PDF file and preserve page information."""

    pdf_path = Path(file_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("The selected file must be a PDF.")

    reader = PdfReader(pdf_path)

    text_parts = []
    page_texts = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()

        if page_text:
            clean_text = page_text.strip()

            text_parts.append(clean_text)

            page_texts.append({
                "page": page_number,
                "text": clean_text
            })

    document_text = "\n".join(text_parts)

    if not document_text.strip():
        raise ValueError("No readable text was found in the PDF.")

    return document_text, page_texts


def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into smaller overlapping chunks."""

    words = text.split()

    if not words:
        return []

    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size

        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap

    return chunks


def chunk_pages(page_texts, chunk_size=500, overlap=50):
    """Create chunks while preserving PDF page numbers."""

    chunks = []
    metadatas = []

    for page_data in page_texts:
        page_number = page_data["page"]
        page_text = page_data["text"]

        page_chunks = chunk_text(
            page_text,
            chunk_size=chunk_size,
            overlap=overlap
        )

        for chunk in page_chunks:
            chunks.append(chunk)

            metadatas.append({
                "page": page_number
            })

    return chunks, metadatas