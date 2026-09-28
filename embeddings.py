from sentence_transformers import SentenceTransformer


# =====================================================
# EMBEDDING MODEL
# =====================================================

MODEL_NAME = "all-MiniLM-L6-v2"


try:
    model = SentenceTransformer(
        MODEL_NAME
    )

except Exception as e:
    raise RuntimeError(
        f"Could not load embedding model: {MODEL_NAME}"
    ) from e


# =====================================================
# CREATE EMBEDDINGS
# =====================================================

def create_embeddings(chunks):
    """
    Convert text chunks into normalized
    numerical embeddings.
    """

    if chunks is None:
        raise ValueError(
            "Chunks cannot be None."
        )


    if not isinstance(chunks, list):
        raise ValueError(
            "Chunks must be provided as a list."
        )


    if not chunks:
        return []


    # Validate and clean text chunks
    cleaned_chunks = []


    for chunk in chunks:

        if not isinstance(chunk, str):
            raise ValueError(
                "Every chunk must be a string."
            )


        clean_chunk = chunk.strip()


        if clean_chunk:
            cleaned_chunks.append(
                clean_chunk
            )


    if not cleaned_chunks:
        return []


    try:
        embeddings = model.encode(
            cleaned_chunks,
            normalize_embeddings=True,
            show_progress_bar=False
        )

    except Exception as e:
        raise RuntimeError(
            "Failed to create embeddings."
        ) from e


    return embeddings.tolist()