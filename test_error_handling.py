import os
import subprocess
import sys
import io
import main

from unittest.mock import patch
from pypdf import PdfWriter
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
from document_reader import read_pdf
from research_agent import generate_rag_answer
from retriever import retrieve_relevant_chunks
from vector_store import search_chunks


# =========================================================
# Helper
# =========================================================

def run_main_with_input(user_input):
    """Run main.py and provide automatic keyboard input."""

    result = subprocess.run(
        [sys.executable, "main.py"],
        input=user_input,
        text=True,
        capture_output=True,
        timeout=60
    )

    return result.stdout + result.stderr


# =========================================================
# BASIC ERROR HANDLING TESTS
# =========================================================

def test_empty_question():
    """Check that an empty research question is handled correctly."""

    output = run_main_with_input("\n")

    expected_message = "Please enter a valid research question."

    if expected_message in output:
        print("PASS: Empty question handled correctly.")
    else:
        print("FAIL: Empty question was not handled correctly.")
        print(output)


def test_invalid_pdf_number():
    """Check that an invalid PDF number is handled correctly."""

    user_input = (
        "What is the capital of France?\n"
        "9\n"
    )

    output = run_main_with_input(user_input)

    expected_message = "Invalid PDF selection: 9"

    if expected_message in output:
        print("PASS: Invalid PDF number handled correctly.")
    else:
        print("FAIL: Invalid PDF number was not handled correctly.")
        print(output)


def test_invalid_pdf_format():
    """Check that non-numeric PDF input is handled correctly."""

    user_input = (
        "What is the capital of France?\n"
        "abc\n"
    )

    output = run_main_with_input(user_input)

    expected_message = "Please enter valid PDF numbers."

    if expected_message in output:
        print("PASS: Invalid PDF format handled correctly.")
    else:
        print("FAIL: Invalid PDF format was not handled correctly.")
        print(output)


def test_empty_pdf_selection():
    """Check that empty PDF selection is handled correctly."""

    user_input = (
        "What is the capital of France?\n"
        "\n"
    )

    output = run_main_with_input(user_input)

    expected_message = "Please enter valid PDF numbers."

    if expected_message in output:
        print("PASS: Empty PDF selection handled correctly.")
    else:
        print("FAIL: Empty PDF selection was not handled correctly.")
        print(output)


def test_missing_pdf():
    """Check that a missing PDF file is handled correctly."""

    try:
        read_pdf("missing_test_file.pdf")

        print("FAIL: Missing PDF was not handled correctly.")

    except FileNotFoundError:
        print("PASS: Missing PDF handled correctly.")


def test_wrong_file_type():
    """Check that a non-PDF file is rejected correctly."""

    test_file = "temporary_test_file.txt"

    with open(test_file, "w", encoding="utf-8") as file:
        file.write("This is only a test file.")

    try:
        read_pdf(test_file)

        print("FAIL: Wrong file type was not handled correctly.")

    except ValueError:
        print("PASS: Wrong file type handled correctly.")

    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


# =========================================================
# ADVANCED ERROR HANDLING TESTS
# =========================================================

# Test 7
def test_empty_pdf():
    """Check that a PDF with no readable text is handled correctly."""

    test_file = "temporary_empty_test.pdf"

    writer = PdfWriter()
    writer.add_blank_page(
        width=300,
        height=300
    )

    with open(test_file, "wb") as file:
        writer.write(file)

    try:
        read_pdf(test_file)

        print("FAIL: Empty PDF was not handled correctly.")

    except ValueError:
        print("PASS: Empty PDF handled correctly.")

    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


# Test 8
def test_openai_api_failure():
    """Check that an OpenAI API failure is handled correctly."""

    with patch(
        "research_agent.client.responses.create",
        side_effect=Exception("Simulated API failure")
    ):

        result = generate_rag_answer(
            "This is a test prompt."
        )

    if "RAG research failed" in result:
        print("PASS: OpenAI API failure handled correctly.")
    else:
        print("FAIL: OpenAI API failure was not handled correctly.")
        print(result)


# Test 9
def test_api_timeout():
    """Check that an API timeout is handled correctly."""

    with patch(
        "research_agent.client.responses.create",
        side_effect=TimeoutError("Simulated API timeout")
    ):

        result = generate_rag_answer(
            "This is a timeout test."
        )

    if "RAG research failed" in result:
        print("PASS: API timeout handled correctly.")
    else:
        print("FAIL: API timeout was not handled correctly.")
        print(result)


# Test 10
def test_vector_database_failure():
    """Check that a vector database failure can be detected."""

    with patch(
        "vector_store.collection.query",
        side_effect=Exception(
            "Simulated vector database failure"
        )
    ):

        try:
            search_chunks(
                question="Test question",
                source_name="Detect AI.pdf",
                top_k=3
            )

            print(
                "FAIL: Vector database failure "
                "was not detected."
            )

        except Exception:
            print(
                "PASS: Vector database failure "
                "detected correctly."
            )


# Test 11
def test_no_retrieved_chunks():
    """Check behaviour when retrieval returns no chunks."""

    with patch(
        "retriever.search_chunks",
        return_value=([], [], [])
    ):

        chunks, metadatas, distances = (
            retrieve_relevant_chunks(
                question="Test question",
                source_name="Detect AI.pdf",
                top_k=3
            )
        )

    if (
        chunks == []
        and metadatas == []
        and distances == []
    ):
        print(
            "PASS: Empty retrieval result "
            "handled correctly."
        )

    else:
        print(
            "FAIL: Empty retrieval result "
            "was not handled correctly."
        )

def test_retrieval_failure_in_main():
    """Check that main.py handles retrieval failure without crashing."""

    fake_pdf = Path("Detect AI.pdf")

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
        side_effect=Exception("Simulated retrieval failure")
    ):

        output = io.StringIO()

        with redirect_stdout(output):
            main.run_pdf_research(
                "What is the main purpose of the Detect AI project?"
            )

        result = output.getvalue()

    if "Retrieval failed for Detect AI.pdf" in result:
        print("PASS: Retrieval failure handled gracefully.")
    else:
        print("FAIL: Retrieval failure was not handled gracefully.")
        print(result)

# =========================================================
# RUN ALL TESTS
# =========================================================

if __name__ == "__main__":

    print("\n--- BASIC ERROR HANDLING ---")

    test_empty_question()
    test_invalid_pdf_number()
    test_invalid_pdf_format()
    test_empty_pdf_selection()
    test_missing_pdf()
    test_wrong_file_type()

    print("\n--- ADVANCED ERROR HANDLING ---")

    test_empty_pdf()
    test_openai_api_failure()
    test_api_timeout()
    test_vector_database_failure()
    test_no_retrieved_chunks()
    test_retrieval_failure_in_main()