from retriever import retrieve_relevant_chunks


# PDFs that belong to the real research knowledge base
SOURCE_FILES = [
    "Detect AI.pdf",
    "Packing List UK.pdf",
    "test.pdf"
]


# Retrieval evaluation test cases
TEST_CASES = [
    {
        "id": "D01",
        "question": "What is the main purpose of the Detect AI project?",
        "expected": {
            "Detect AI.pdf": [1]
        }
    },
    {
        "id": "D02",
        "question": "Which model is used for the premium Detect AI tier, and how was it trained?",
        "expected": {
            "Detect AI.pdf": [2]
        }
    },
    {
        "id": "D03",
        "question": "What performance metrics are reported for the standard Detect AI model?",
        "expected": {
            "Detect AI.pdf": [2]
        }
    },
    {
        "id": "D04",
        "question": "How does Detect AI limit API abuse?",
        "expected": {
            "Detect AI.pdf": [3]
        }
    },
    {
        "id": "D05",
        "question": "What tools are used for monitoring in the Kubernetes-based local environment?",
        "expected": {
            "Detect AI.pdf": [4]
        }
    },
    {
        "id": "D06",
        "question": "How much did Turborepo reduce task execution time?",
        "expected": {
            "Detect AI.pdf": [1]
        }
    },

    {
        "id": "P01",
        "question": "What size pressure cooker does the UK packing guide recommend?",
        "expected": {
            "Packing List UK.pdf": [1]
        }
    },
    {
        "id": "P02",
        "question": "Why does the packing guide recommend carrying an umbrella?",
        "expected": {
            "Packing List UK.pdf": [1]
        }
    },
    {
        "id": "P03",
        "question": "How many travel adapters does the packing guide recommend?",
        "expected": {
            "Packing List UK.pdf": [1]
        }
    },
    {
        "id": "P04",
        "question": "Which key travel documents are listed in the packing guide?",
        "expected": {
            "Packing List UK.pdf": [2]
        }
    },
    {
        "id": "P05",
        "question": "What quantities of rice and toor dal are recommended?",
        "expected": {
            "Packing List UK.pdf": [2]
        }
    },
    {
        "id": "P06",
        "question": "What does the guide recommend about bedsheets?",
        "expected": {
            "Packing List UK.pdf": [2]
        }
    },

    {
        "id": "H01",
        "question": "What is the minimum age to enter the HSBC prize draw?",
        "expected": {
            "test.pdf": [1]
        }
    },
    {
        "id": "H02",
        "question": "When does entry to the HSBC prize draw close?",
        "expected": {
            "test.pdf": [2]
        }
    },
    {
        "id": "H03",
        "question": "What cash prizes are available in the HSBC prize draw?",
        "expected": {
            "test.pdf": [2]
        }
    },
    {
        "id": "H04",
        "question": "By when will HSBC select the prize draw winners?",
        "expected": {
            "test.pdf": [2]
        }
    },
    {
        "id": "H05",
        "question": "How long do winners have to reply to the winner email?",
        "expected": {
            "test.pdf": [3]
        }
    },
    {
        "id": "H06",
        "question": "Which accessibility formats does HSBC say are available?",
        "expected": {
            "test.pdf": [4]
        }
    },

    # Multi-source questions
    {
        "id": "M01",
        "question": (
            "What does Detect AI use for human verification, "
            "and how many travel adapters does the UK packing guide recommend?"
        ),
        "expected": {
            "Detect AI.pdf": [1],
            "Packing List UK.pdf": [2]
        }
    },
    {
        "id": "M02",
        "question": (
            "What accuracy did the Detect AI premium model achieve, "
            "and what are the HSBC grand prizes?"
        ),
        "expected": {
            "Detect AI.pdf": [2],
            "test.pdf": [2]
        }
    },
    {
        "id": "M03",
        "question": (
            "Why does the packing guide recommend an umbrella, "
            "and what accessibility formats does HSBC offer?"
        ),
        "expected": {
            "Packing List UK.pdf": [1],
            "test.pdf": [4]
        }
    }
]


def retrieve_from_all_sources(question, top_k_per_source=2):
    """Retrieve chunks from all research PDFs and rank them together."""

    combined_results = []

    for source_name in SOURCE_FILES:

        chunks, metadatas, distances = retrieve_relevant_chunks(
            question=question,
            source_name=source_name,
            top_k=top_k_per_source
        )

        for chunk, metadata, distance in zip(
            chunks,
            metadatas,
            distances
        ):
            combined_results.append(
                (
                    chunk,
                    metadata,
                    distance
                )
            )

    # Smaller distance means more relevant
    combined_results.sort(
        key=lambda item: item[2]
    )

    # Same idea as our main mixed-ranking system
    return combined_results[:3]


def evaluate_test(test):
    """Evaluate one retrieval question."""

    results = retrieve_from_all_sources(
        test["question"]
    )

    print("\n" + "=" * 70)
    print(f"Test: {test['id']}")
    print(f"Question: {test['question']}")

    print("\nTop retrieved results:")

    for rank, (_, metadata, distance) in enumerate(
        results,
        start=1
    ):
        print(
            f"{rank}. "
            f"{metadata['source']} | "
            f"Page {metadata['page']} | "
            f"Distance {distance:.4f}"
        )

    expected = test["expected"]

    source_hits = {}
    page_hits = {}

    reciprocal_ranks = []

    for expected_source, expected_pages in expected.items():

        source_hit = False
        page_hit = False
        first_correct_rank = None

        for rank, (_, metadata, _) in enumerate(
            results,
            start=1
        ):

            source = metadata.get("source")
            page = metadata.get("page")

            if source == expected_source:
                source_hit = True

                if first_correct_rank is None:
                    first_correct_rank = rank

                if page in expected_pages:
                    page_hit = True

        source_hits[expected_source] = source_hit
        page_hits[expected_source] = page_hit

        if first_correct_rank is not None:
            reciprocal_ranks.append(
                1 / first_correct_rank
            )
        else:
            reciprocal_ranks.append(0)

    source_pass = all(source_hits.values())
    page_pass = all(page_hits.values())

    if reciprocal_ranks:
        test_mrr = sum(reciprocal_ranks) / len(
            reciprocal_ranks
        )
    else:
        test_mrr = 0

    print("\nEvaluation:")

    print(
        f"Source Hit@3: "
        f"{'PASS' if source_pass else 'FAIL'}"
    )

    print(
        f"Page Hit@3: "
        f"{'PASS' if page_pass else 'FAIL'}"
    )

    print(
        f"MRR: {test_mrr:.3f}"
    )

    return {
        "source_pass": source_pass,
        "page_pass": page_pass,
        "mrr": test_mrr
    }


def main():
    """Run the complete retrieval evaluation."""

    total_tests = len(TEST_CASES)

    source_passes = 0
    page_passes = 0

    total_mrr = 0

    print("\n======================================")
    print(" AI Research Agent Retrieval Evaluation")
    print("======================================")

    for test in TEST_CASES:

        result = evaluate_test(test)

        if result["source_pass"]:
            source_passes += 1

        if result["page_pass"]:
            page_passes += 1

        total_mrr += result["mrr"]

    source_accuracy = (
        source_passes / total_tests
    ) * 100

    page_accuracy = (
        page_passes / total_tests
    ) * 100

    average_mrr = (
        total_mrr / total_tests
    )

    print("\n")
    print("=" * 70)
    print("FINAL RETRIEVAL EVALUATION")
    print("=" * 70)

    print(f"Total tests: {total_tests}")

    print(
        f"Source Hit@3: "
        f"{source_passes}/{total_tests} "
        f"({source_accuracy:.2f}%)"
    )

    print(
        f"Page Hit@3: "
        f"{page_passes}/{total_tests} "
        f"({page_accuracy:.2f}%)"
    )

    print(
        f"Mean Reciprocal Rank (MRR): "
        f"{average_mrr:.3f}"
    )


if __name__ == "__main__":
    main()
    
def diagnostic_check(question, expected_source=None, expected_page=None):
    """Print detailed retrieval results for debugging."""

    print("\n" + "=" * 70)
    print("DIAGNOSTIC CHECK")
    print("=" * 70)

    print(f"Question: {question}")

    if expected_source:
        print(f"Expected source: {expected_source}")

    if expected_page:
        print(f"Expected page: {expected_page}")

    print("\nDetailed results:")

    all_results = []

    for source_name in SOURCE_FILES:

        chunks, metadatas, distances = retrieve_relevant_chunks(
            question=question,
            source_name=source_name,
            top_k=5
        )

        for chunk, metadata, distance in zip(
            chunks,
            metadatas,
            distances
        ):
            all_results.append(
                (
                    chunk,
                    metadata,
                    distance
                )
            )

    all_results.sort(
        key=lambda item: item[2]
    )

    for rank, (chunk, metadata, distance) in enumerate(
        all_results,
        start=1
    ):

        print(
            f"\nRank {rank}"
        )

        print(
            f"Source: {metadata.get('source')}"
        )

        print(
            f"Page: {metadata.get('page')}"
        )

        print(
            f"Chunk index: {metadata.get('chunk_index')}"
        )

        print(
            f"Distance: {distance:.4f}"
        )

        print(
            f"Text preview: {chunk[:250]}..."
        )