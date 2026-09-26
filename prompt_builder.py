def build_rag_prompt(question, relevant_chunks, metadatas):
    """Build a clean RAG prompt using retrieved PDF context."""

    if not relevant_chunks:
        return None

    context_parts = []

    for chunk, metadata in zip(
        relevant_chunks,
        metadatas
    ):

        source = metadata.get(
            "source",
            "Unknown source"
        )

        page = metadata.get(
            "page",
            "Unknown"
        )

        context_parts.append(
            f"[Source: {source}, Page: {page}]\n"
            f"{chunk}"
        )

    context = "\n\n".join(
        context_parts
    )

    prompt = f"""
You are an AI research assistant.

Answer the user's question using ONLY the document context provided below.

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}


INSTRUCTIONS:

1. Use only information supported by the provided document context.

2. Do not use outside knowledge.

3. Do not invent, assume, or guess information.

4. If the answer cannot be found in the provided documents,
   reply exactly:

   "I could not find this information in the provided documents."


ANSWER QUALITY:

- Answer the user's question directly.
- Keep the answer clear, accurate, natural, and professional.
- Include enough explanation to properly answer the question.
- Avoid unnecessary repetition.
- Do not add unrelated information.
- Preserve important technical terms from the documents.


FORMATTING:

- Format the answer according to the type of question.
- Use short paragraphs for normal explanations.
- Use bullet points when several separate points need to be explained.
- Use numbered steps when the question asks for a process or procedure.
- Use clear Markdown headings only when they genuinely improve readability.
- Use **bold text** for important terms when useful.
- Keep the formatting simple and professional.
- Do not force the same structure for every answer.


EQUATIONS:

- If equations or formulas are relevant, place them on separate lines.
- Use clean Markdown formatting.
- Do not place equations inside unnecessary square brackets.
- Briefly explain what the equation means when needed.


CITATIONS:

- Cite factual information using the PDF filename and page number.
- Put citations close to the information they support.
- Use citation formats such as:

  (Source: filename.pdf, p. 3)

  or

  (Source: filename.pdf, pp. 3–5)

- Do not mention chunk numbers in the final answer.
- Do not cite documents that were not actually used.


SOURCES:

At the end of the answer, add:

### Sources

List only the PDF files and page numbers actually used.

Keep the Sources section concise.
"""

    return prompt