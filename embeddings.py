from threading import Lock

from sentence_transformers import SentenceTransformer


# =====================================================
# EMBEDDING MODEL
# =====================================================

MODEL_NAME = "all-MiniLM-L6-v2"

_model = None
_model_lock = Lock()


def get_model():
    """
    Load the SentenceTransformer model only when
    it is actually needed.
    """

    global _model

    if _model is None:

        with _model_lock:

            if _model is None:

                try:
                    _model = SentenceTransformer(
                        MODEL_NAME
                    )

                except Exception as e:
                    raise RuntimeError(
                        f"Could not load embedding model: {MODEL_NAME}"
                    ) from e

    return _model


# =====================================================
# LAZY MODEL COMPATIBILITY
# =====================================================

class LazyEmbeddingModel:
    """
    Keeps compatibility with existing code that uses:

    from embeddings import model

    The real model is loaded only when it is used.
    """

    def __getattr__(self, name):
        return getattr(
            get_model(),
            name
        )


model = LazyEmbeddingModel()


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
        embedding_model = get_model()

        embeddings = embedding_model.encode(
            cleaned_chunks,
            normalize_embeddings=True,
            show_progress_bar=False
        )

    except Exception as e:
        raise RuntimeError(
            "Failed to create embeddings."
        ) from e

    return embeddings.tolist()