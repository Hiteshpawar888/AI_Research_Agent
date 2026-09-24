def build_rag_prompt(question, relevant_chunks, metadatas):
    """Build a RAG prompt using retrieved chunks and source metadata."""

    if not relevant_chunks:
        return None

    context_parts = []

    for chunk, metadata in zip(relevant_chunks, metadatas):
        source = metadata.get("source", "Unknown source")
        page = metadata.get("page", "Unknown")
        chunk_index = metadata.get("chunk_index", "Unknown")

        context_parts.append(
            f"[Source: {source}, Page: {page}, Chunk: {chunk_index}]\n{chunk}"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
Answer the user's question using only the context below.

Context:
{context}

Question:
{question}

Instructions:
- Use only information from the provided context.
- Do not use outside knowledge.
- Do not invent or guess information.
- If the answer is not available in the provided context, reply exactly:
  "I could not find this information in the provided documents."
- If the answer is not found, do not cite unrelated sources or pages.
- Keep the answer clear and concise.
- Cite the source and page number for factual information.
- Add a "Sources" section at the end listing only the sources and page numbers actually used.
"""

    return prompt