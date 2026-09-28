from vector_store import search_chunks


def retrieve_relevant_chunks(
    question,
    source_name,
    session_id,
    top_k=2
):
    """
    Retrieve relevant chunks only from
    the selected document and current session.
    """

    # Validate inputs
    if not question or not question.strip():
        raise ValueError(
            "Question cannot be empty."
        )

    if not source_name:
        raise ValueError(
            "Source name is required."
        )

    if not session_id:
        raise ValueError(
            "Session ID is required."
        )

    if not isinstance(top_k, int) or top_k < 1:
        raise ValueError(
            "top_k must be a positive integer."
        )

    # Search only within the selected source
    # and the current user's session
    relevant_chunks, metadatas, distances = search_chunks(
        question=question.strip(),
        source_name=source_name,
        session_id=session_id,
        top_k=top_k
    )

    # Safe empty-result handling
    if not relevant_chunks:
        return [], [], []

    return (
        relevant_chunks,
        metadatas,
        distances
    )