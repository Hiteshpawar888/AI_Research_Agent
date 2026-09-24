import io

from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import main
import research_agent

from main import select_tool
from retriever import retrieve_relevant_chunks
from prompt_builder import build_rag_prompt


# =========================================================
# TEST 1: TOOL ROUTING
# =========================================================

def test_tool_routing():
    """Check PDF, Web and Both routing."""

    pdf_question = (
        "What does the uploaded PDF say about the project?"
    )

    web_question = (
        "What is the latest AI news today?"
    )

    both_question = (
        "Compare this uploaded PDF with the latest information online."
    )

    pdf_result = select_tool(pdf_question)
    web_result = select_tool(web_question)
    both_result = select_tool(both_question)

    if (
        pdf_result == "pdf"
        and web_result == "web"
        and both_result == "both"
    ):
        print("PASS: Tool routing works correctly.")

    else:
        print("FAIL: Tool routing failed.")
        print("PDF result:", pdf_result)
        print("Web result:", web_result)
        print("Both result:", both_result)


# =========================================================
# TEST 2: PDF RETRIEVAL
# =========================================================

def test_pdf_retrieval():
    """Check that the correct PDF content is retrieved."""

    question = (
        "What cash prizes are available "
        "in the HSBC prize draw?"
    )

    chunks, metadatas, distances = retrieve_relevant_chunks(
        question,
        source_name="test.pdf",
        top_k=3
    )

    if not chunks:
        print("FAIL: PDF retrieval returned no chunks.")
        return

    retrieved_sources = [
        metadata.get("source")
        for metadata in metadatas
    ]

    retrieved_pages = [
        metadata.get("page")
        for metadata in metadatas
    ]

    if (
        "test.pdf" in retrieved_sources
        and 2 in retrieved_pages
    ):
        print(
            "PASS: PDF retrieval returned "
            "the correct source and page."
        )

    else:
        print("FAIL: PDF retrieval result was incorrect.")
        print("Sources:", retrieved_sources)
        print("Pages:", retrieved_pages)


# =========================================================
# TEST 3: WEB RESEARCH
# =========================================================

def test_web_research():
    """
    Check the web research flow without making
    a real API/web request.
    """

    fake_answer = (
        "This is a simulated web research answer."
    )

    with patch(
        "main.generate_answer",
        return_value=fake_answer
    ):

        output = io.StringIO()

        with redirect_stdout(output):
            main.run_web_research(
                "What is the latest AI news today?"
            )

        result = output.getvalue()

    if fake_answer in result:
        print("PASS: Web research pipeline works correctly.")

    else:
        print("FAIL: Web research pipeline failed.")
        print(result)


# =========================================================
# TEST 4: PROMPT + CITATION METADATA
# =========================================================

def test_prompt_and_citation():
    """Check that source and page metadata enter the RAG prompt."""

    question = (
        "What cash prizes are available "
        "in the HSBC prize draw?"
    )

    chunks = [
        (
            "There are 2 grand prizes of £10,000 "
            "and 5 runner-up prizes of £1,000."
        )
    ]

    metadatas = [
        {
            "source": "test.pdf",
            "page": 2,
            "chunk_index": 1
        }
    ]

    prompt = build_rag_prompt(
        question,
        chunks,
        metadatas
    )

    if (
        prompt is not None
        and "test.pdf" in prompt
        and "Page: 2" in prompt
        and question in prompt
        and "£10,000" in prompt
    ):
        print(
            "PASS: Prompt and citation metadata "
            "built correctly."
        )

    else:
        print(
            "FAIL: Prompt or citation metadata "
            "was incorrect."
        )

        print(prompt)


# =========================================================
# TEST 5: RAG ANSWER GENERATION
# =========================================================

def test_rag_generation():
    """
    Check generate_rag_answer without making
    a real OpenAI API call.
    """

    fake_response = SimpleNamespace(
        output_text="Mock RAG answer.",
        usage=SimpleNamespace(
            input_tokens=100,
            output_tokens=20,
            total_tokens=120
        )
    )

    with patch(
        "research_agent.client.responses.create",
        return_value=fake_response
    ):

        result = research_agent.generate_rag_answer(
            "This is a test RAG prompt."
        )

    if result == "Mock RAG answer.":
        print(
            "PASS: RAG answer generation "
            "works correctly."
        )

    else:
        print(
            "FAIL: RAG answer generation failed."
        )

        print(result)


# =========================================================
# TEST 6: END-TO-END PDF PIPELINE
# =========================================================

def test_end_to_end_pdf_pipeline():
    """
    Check PDF selection -> retrieval -> prompt ->
    answer flow without a real OpenAI API call.
    """

    fake_pdf = Path("test.pdf")

    fake_chunks = [
        (
            "There are 2 grand prizes of £10,000 "
            "and 5 runner-up prizes of £1,000."
        )
    ]

    fake_metadatas = [
        {
            "source": "test.pdf",
            "page": 2,
            "chunk_index": 1
        }
    ]

    fake_distances = [0.25]

    fake_final_answer = (
        "There are 2 grand prizes of £10,000 "
        "and 5 runner-up prizes of £1,000. "
        "[Source: test.pdf, Page 2]"
    )

    with patch(
        "main.Path.glob",
        return_value=[fake_pdf]
    ), patch(
        "builtins.input",
        return_value="1"
    ), patch(
        "main.is_document_indexed",
        return_value=True
    ), patch(
        "main.retrieve_relevant_chunks",
        return_value=(
            fake_chunks,
            fake_metadatas,
            fake_distances
        )
    ), patch(
        "main.generate_rag_answer",
        return_value=fake_final_answer
    ):

        output = io.StringIO()

        with redirect_stdout(output):

            main.run_pdf_research(
                (
                    "What cash prizes are available "
                    "in the HSBC prize draw?"
                )
            )

        result = output.getvalue()

    if (
        fake_final_answer in result
        and "test.pdf" in result
        and "Page: 2" in result
    ):
        print(
            "PASS: End-to-end PDF pipeline "
            "works correctly."
        )

    else:
        print(
            "FAIL: End-to-end PDF pipeline failed."
        )

        print(result)


# =========================================================
# RUN ALL AUTOMATED PIPELINE TESTS
# =========================================================

if __name__ == "__main__":

    print("\n--- 1. TOOL ROUTING ---")
    test_tool_routing()

    print("\n--- 2. PDF RETRIEVAL ---")
    test_pdf_retrieval()

    print("\n--- 3. WEB RESEARCH ---")
    test_web_research()

    print("\n--- 4. PROMPT + CITATION ---")
    test_prompt_and_citation()

    print("\n--- 5. RAG GENERATION ---")
    test_rag_generation()

    print("\n--- 6. END-TO-END PDF PIPELINE ---")
    test_end_to_end_pdf_pipeline()