from vector_store import search_chunks


def retrieve_relevant_chunks(question, source_name, top_k=2):
    """Retrieve chunks, metadata, and relevance distances."""

    relevant_chunks, metadatas, distances = search_chunks(
        question=question,
        source_name=source_name,
        top_k=top_k
    )

    return relevant_chunks, metadatas, distances