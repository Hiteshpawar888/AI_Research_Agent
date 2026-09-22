from sentence_transformers import SentenceTransformer


model = SentenceTransformer("all-MiniLM-L6-v2")


def create_embeddings(chunks):
    """Convert text chunks into numerical embeddings."""

    if not chunks:
        return []

    embeddings = model.encode(chunks)

    return embeddings