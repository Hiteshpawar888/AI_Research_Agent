from pathlib import Path

from pypdf import PdfReader


# =====================================================
# READ PDF
# =====================================================

def read_pdf(file_path):
    """
    Extract readable text from a PDF
    while preserving page numbers.
    """

    pdf_path = Path(file_path)


    # Validate file existence
    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {file_path}"
        )


    if not pdf_path.is_file():
        raise ValueError(
            "The selected PDF path is not a file."
        )


    # Validate extension
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(
            "The selected file must be a PDF."
        )


    # Open PDF safely
    try:
        reader = PdfReader(
            str(pdf_path)
        )

    except Exception as e:
        raise ValueError(
            "The PDF could not be opened or may be corrupted."
        ) from e


    # Reject encrypted/password-protected PDFs
    if reader.is_encrypted:
        raise ValueError(
            "Password-protected PDFs are not supported."
        )


    # Validate that PDF contains pages
    if len(reader.pages) == 0:
        raise ValueError(
            "The PDF does not contain any pages."
        )


    text_parts = []
    page_texts = []


    # Extract page-by-page text
    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        try:
            page_text = page.extract_text()

        except Exception:
            # Skip an unreadable page instead
            # of crashing the entire document
            continue


        if not page_text:
            continue


        clean_text = page_text.strip()


        if not clean_text:
            continue


        text_parts.append(
            clean_text
        )


        page_texts.append(
            {
                "page": page_number,
                "text": clean_text
            }
        )


    document_text = "\n".join(
        text_parts
    )


    # No usable text in PDF
    if not document_text.strip():
        raise ValueError(
            "No readable text was found in the PDF."
        )


    return document_text, page_texts


# =====================================================
# CHUNK PLAIN TEXT
# =====================================================

def chunk_text(
    text,
    chunk_size=500,
    overlap=50
):
    """
    Split text into overlapping word-based chunks.
    """

    if not isinstance(text, str):
        raise ValueError(
            "Text must be a string."
        )


    if not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError(
            "chunk_size must be a positive integer."
        )


    if not isinstance(overlap, int) or overlap < 0:
        raise ValueError(
            "overlap must be a non-negative integer."
        )


    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size."
        )


    words = text.split()


    if not words:
        return []


    chunks = []

    start = 0


    while start < len(words):

        end = min(
            start + chunk_size,
            len(words)
        )


        chunk = " ".join(
            words[start:end]
        ).strip()


        if chunk:
            chunks.append(
                chunk
            )


        # Finished document
        if end >= len(words):
            break


        start = end - overlap


    return chunks


# =====================================================
# CHUNK PDF PAGES
# =====================================================

def chunk_pages(
    page_texts,
    chunk_size=500,
    overlap=50
):
    """
    Create chunks while preserving
    the original PDF page number.
    """

    if not page_texts:
        return [], []


    chunks = []
    metadatas = []


    for page_data in page_texts:

        if not isinstance(
            page_data,
            dict
        ):
            continue


        page_number = page_data.get(
            "page"
        )


        page_text = page_data.get(
            "text",
            ""
        )


        # Skip invalid or empty pages
        if page_number is None:
            continue


        if not isinstance(page_text, str):
            continue


        if not page_text.strip():
            continue


        page_chunks = chunk_text(
            page_text,
            chunk_size=chunk_size,
            overlap=overlap
        )


        for chunk in page_chunks:

            chunks.append(
                chunk
            )


            metadatas.append(
                {
                    "page": page_number
                }
            )


    return chunks, metadatas