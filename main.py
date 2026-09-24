from pathlib import Path
from research_agent import (generate_answer, generate_rag_answer, generate_combined_answer)
from document_reader import read_pdf, chunk_pages
from retriever import retrieve_relevant_chunks
from prompt_builder import build_rag_prompt
from vector_store import store_chunks, is_document_indexed

def run_combined_research(question):
    """Research using selected PDFs together with live web search."""

    pdf_files = list(Path(".").glob("*.pdf"))

    if not pdf_files:
        print("No PDF files were found in the project folder.")
        return

    print("\nAvailable PDF files:")

    for index, pdf_file in enumerate(pdf_files, start=1):
        print(f"{index}. {pdf_file.name}")

    choice = input(
        "\nChoose PDF number(s), separated by commas (example: 1,2): "
    ).strip()

    try:
        selected_numbers = [
            int(number.strip())
            for number in choice.split(",")
        ]
    except ValueError:
        print("Please enter valid PDF numbers.")
        return

    selected_numbers = list(dict.fromkeys(selected_numbers))

    for number in selected_numbers:
        if number < 1 or number > len(pdf_files):
            print(f"Invalid PDF selection: {number}")
            return

    selected_files = [
        pdf_files[number - 1]
        for number in selected_numbers
    ]

    print("\nSelected PDF files:")

    for pdf_file in selected_files:
        print(f"- {pdf_file.name}")

    # Index PDFs if they are not already stored
    for pdf_file in selected_files:
        file_path = str(pdf_file)

        try:
            if is_document_indexed(file_path):
                print(
                    f"{pdf_file.name} already indexed. "
                    "Skipping embedding process."
                )

            else:
                _, page_texts = read_pdf(file_path)

                chunks, page_metadatas = chunk_pages(
                    page_texts
                )

                store_chunks(
                    chunks,
                    file_path,
                    page_metadatas
                )

                print(
                    f"{pdf_file.name} indexed successfully."
                )

        except FileNotFoundError as e:
            print(f"PDF file not found: {e}")
            return

        except ValueError as e:
            print(f"PDF processing error: {e}")
            return

        except Exception as e:
            print(f"Unexpected error while processing {pdf_file.name}: {e}")
            return

    # Retrieve relevant chunks
    all_chunks = []
    all_metadatas = []
    all_distances = []

    for pdf_file in selected_files:
        chunks, metadatas, distances = retrieve_relevant_chunks(
            question,
            str(pdf_file),
            top_k=2
        )

        all_chunks.extend(chunks)
        all_metadatas.extend(metadatas)
        all_distances.extend(distances)

    if not all_chunks:
        print("No relevant PDF content was found.")
        return

    # Mixed ranking
    combined_results = list(
        zip(
            all_chunks,
            all_metadatas,
            all_distances
        )
    )

    combined_results.sort(
        key=lambda item: item[2]
    )

    top_results = combined_results[:3]

    # Build PDF context
    context_parts = []

    for chunk, metadata, distance in top_results:
        source = metadata.get("source", "Unknown source")
        page = metadata.get("page", "Unknown")

        context_parts.append(
            f"[PDF Source: {source}, Page: {page}]\n{chunk}"
        )

    pdf_context = "\n\n".join(context_parts)

    # Build combined PDF + Web prompt
    combined_prompt = f"""
Research the user's question using BOTH:
1. The PDF context provided below.
2. Reliable current web sources.

User Question:
{question}

PDF Context:
{pdf_context}

Instructions:
- Use the PDF evidence where relevant.
- Use web search for current or additional information.
- Do not invent information.
- Clearly cite PDF information with the file name and page number.
- Cite web information using the web sources actually used.
- If PDF information and web information disagree, clearly explain the difference.
- Keep the answer concise and professional.
"""

    answer = generate_combined_answer(
        combined_prompt
    )

    print("\nCombined PDF + Web Research Answer:")
    print(answer)

def select_tool(question):
    """Decide whether to use PDF research, web research, or both."""

    question = question.lower().strip()

    pdf_keywords = [
        "pdf",
        "document",
        "file",
        "page",
        "report",
        "uploaded"
    ]

    web_keywords = [
        "latest",
        "today",
        "current",
        "recent",
        "news",
        "online",
        "web",
        "internet"
    ]

    needs_pdf = any(
        keyword in question
        for keyword in pdf_keywords
    )

    needs_web = any(
        keyword in question
        for keyword in web_keywords
    )

    if needs_pdf and needs_web:
        return "both"

    elif needs_web:
        return "web"

    elif needs_pdf:
        return "pdf"

    else:
        return "pdf"

def get_user_question():
    """Take a research question from the user."""
    return input("Enter your research question: ").strip()


def process_question(question):
    """Validate the user's research question."""

    if not question:
        return None

    if len(question) < 5:
        return None

    if "http://" in question or "https://" in question or ".py" in question:
        return None

    return question


def run_web_research(question=None):
    """Run web-based research."""

    if question is None:
        question = get_user_question()
        question = process_question(question)

    if question is None:
        print("Please enter a valid research question.")
        return

    answer = generate_answer(question)

    print("\nAI Research Report:")
    print(answer)


def run_pdf_research(question=None):
    """Run RAG research using one or multiple PDF documents."""

    # Step 1: Find all PDF files
    pdf_files = list(Path(".").glob("*.pdf"))

    if not pdf_files:
        print("No PDF files were found in the project folder.")
        return

    print("\nAvailable PDF files:")

    for index, pdf_file in enumerate(pdf_files, start=1):
        print(f"{index}. {pdf_file.name}")

    # Step 2: Allow multiple PDF selection
    choice = input(
        "\nChoose PDF number(s), separated by commas (example: 1,2): "
    ).strip()

    try:
        selected_numbers = [
            int(number.strip())
            for number in choice.split(",")
        ]

    except ValueError:
        print("Please enter valid PDF numbers.")
        return

    # Remove duplicate selections
    selected_numbers = list(dict.fromkeys(selected_numbers))

    for number in selected_numbers:
        if number < 1 or number > len(pdf_files):
            print(f"Invalid PDF selection: {number}")
            return

    selected_files = [
        pdf_files[number - 1]
        for number in selected_numbers
    ]

    print("\nSelected PDF files:")

    for pdf_file in selected_files:
        print(f"- {pdf_file.name}")

    # Step 3: Index selected PDFs if needed
    for pdf_file in selected_files:

        file_path = str(pdf_file)

        try:
            if is_document_indexed(file_path):
                print(
                    f"{pdf_file.name} already indexed. "
                    "Skipping embedding process."
                )

            else:
                _, page_texts = read_pdf(file_path)

                chunks, page_metadatas = chunk_pages(
                    page_texts
                )

                store_chunks(
                    chunks,
                    file_path,
                    page_metadatas
                )

                print(
                    f"{pdf_file.name} indexed successfully."
                )

        except Exception as e:
            print(
                f"Could not process {pdf_file.name}: {e}"
            )
            return

    # Step 4: Get the research question if not already provided
    if question is None:
        question = get_user_question()
        question = process_question(question)

    if question is None:
        print("Please enter a valid research question.")
        return

        # Step 5: Retrieve relevant chunks from every selected PDF
    all_relevant_chunks = []
    all_metadatas = []
    all_distances = []

    for pdf_file in selected_files:

        try:
            relevant_chunks, metadatas, distances = retrieve_relevant_chunks(
                question,
                str(pdf_file),
                top_k=3
            )

            all_relevant_chunks.extend(relevant_chunks)
            all_metadatas.extend(metadatas)
            all_distances.extend(distances)

        except Exception as e:
            print(f"Retrieval failed for {pdf_file.name}: {e}")
            return

        if not all_relevant_chunks:
            print("No relevant document content was found.")
            return


    # Step 5.1: Mixed ranking across all selected PDFs
    combined_results = list(
        zip(
            all_relevant_chunks,
            all_metadatas,
            all_distances
        )
    )

    combined_results.sort(
        key=lambda item: item[2]
    )

    top_results = combined_results[:3]
    
    print("\n--- Top Mixed-Ranking Results ---")

    for rank, (chunk, metadata, distance) in enumerate(top_results, start=1):
        source = metadata.get("source", "Unknown source")
        page = metadata.get("page", "Unknown")

        print(
            f"{rank}. Source: {source} | "
            f"Page: {page} | "
            f"Distance: {distance:.4f}"
        )

    all_relevant_chunks = [
        item[0] for item in top_results
    ]

    all_metadatas = [
        item[1] for item in top_results
    ]

    # Step 6: Build one combined RAG prompt
    prompt = build_rag_prompt(
        question,
        all_relevant_chunks,
        all_metadatas
    )

    if prompt is None:
        print("Could not build the RAG prompt.")
        return

    # Step 7: Make one OpenAI API call
    answer = generate_rag_answer(prompt)

    print("\nMulti-Source RAG Answer:")
    print(answer)


def main():
    """Run the AI Research Agent with automatic tool selection."""

    print("\n==============================")
    print("      AI Research Agent")
    print("==============================")

    question = get_user_question()
    question = process_question(question)

    if question is None:
        print("Please enter a valid research question.")
        return

    selected_tool = select_tool(question)

    print(f"\nSelected tool: {selected_tool.upper()}")

    if selected_tool == "web":
        print("Routing to Web Research...")
        run_web_research(question)

    elif selected_tool == "pdf":
        print("Routing to PDF Research...")
        run_pdf_research(question)

    elif selected_tool == "both":
        print("Routing to Web + PDF Research...")
        run_combined_research(question)


if __name__ == "__main__":
    main()