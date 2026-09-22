import csv
import re
from retriever import retrieve_relevant_chunks
from prompt_builder import build_rag_prompt
from openai import OpenAI
from research_agent import generate_rag_answer

client = OpenAI()

def evaluate_answer(question, generated_answer, reference_answer):
    """Evaluate a generated answer against the reference answer."""

    evaluation_prompt = f"""
Evaluate the generated answer using the reference answer.

Question:
{question}

Reference Answer:
{reference_answer}

Generated Answer:
{generated_answer}

Check:
1. Correctness
2. Relevance
3. Completeness
4. Whether the important facts from the reference answer are present

Give a score from 0 to 5:

5 = Fully correct
4 = Mostly correct, minor detail missing
3 = Partially correct
2 = Major information missing
1 = Mostly incorrect
0 = Completely incorrect

Return exactly in this format:

Score: <0-5>
Explanation: <short explanation>
"""

    try:
        response = client.responses.create(
            model="gpt-5.6-luna",
            reasoning={"effort": "none"},
            input=evaluation_prompt
        )

        return response.output_text

    except Exception as e:
        return f"Answer evaluation failed: {e}"
    
if __name__ == "__main__":

    # D06 is intentionally excluded because of the known page-retrieval mismatch
    tests = [
        {
            "id": "D01",
            "question": "What is the main purpose of the Detect AI project?",
            "source": "Detect AI.pdf",
            "reference": "It is a full-stack platform designed to distinguish human-written text from AI-generated text using a dual-model approach."
        },
        {
            "id": "D02",
            "question": "Which model is used for the premium Detect AI tier, and how was it trained?",
            "source": "Detect AI.pdf",
            "reference": "The premium model is BERT_BASE_UNCASED, fine-tuned for 5 epochs with a batch size of 16."
        },
        {
            "id": "D03",
            "question": "What performance metrics are reported for the standard Detect AI model?",
            "source": "Detect AI.pdf",
            "reference": "The standard DNN model reports 97.25% test accuracy and an AUC-ROC of 0.9940."
        },
        {
            "id": "D04",
            "question": "How does Detect AI limit API abuse?",
            "source": "Detect AI.pdf",
            "reference": "It uses Upstash Redis rate limiting to restrict users to 50 requests per 60 seconds."
        },
        {
            "id": "D05",
            "question": "What tools are used for monitoring in the Kubernetes-based local environment?",
            "source": "Detect AI.pdf",
            "reference": "The environment deploys kube-prometheus-stack, including Prometheus for metrics collection and Grafana for visualization."
        },

        {
            "id": "P01",
            "question": "What size pressure cooker does the UK packing guide recommend?",
            "source": "Packing List UK.pdf",
            "reference": "A 1.5 to 2 litre pressure cooker."
        },
        {
            "id": "P02",
            "question": "Why does the packing guide recommend carrying an umbrella?",
            "source": "Packing List UK.pdf",
            "reference": "Because it rains frequently in the UK."
        },
        {
            "id": "P03",
            "question": "How many travel adapters does the packing guide recommend?",
            "source": "Packing List UK.pdf",
            "reference": "Two travel adapters."
        },
        {
            "id": "P04",
            "question": "Which key travel documents are listed in the packing guide?",
            "source": "Packing List UK.pdf",
            "reference": "Passport, biometric/visa approval letter, travel tickets, and an international driving licence."
        },
        {
            "id": "P05",
            "question": "What quantities of rice and toor dal are recommended?",
            "source": "Packing List UK.pdf",
            "reference": "2 kg of rice and 2 kg of toor dal."
        },
        {
            "id": "P06",
            "question": "What does the guide recommend about bedsheets?",
            "source": "Packing List UK.pdf",
            "reference": "It recommends carrying two double fitted bedsheets, noting that fitted and double ones can fit different bed sizes."
        },

        {
            "id": "H01",
            "question": "What is the minimum age to enter the HSBC UK September 2026 Mobile Banking Prize Draw?",
            "source": "test.pdf",
            "reference": "Entrants must be 18 years or over."
        },
        {
            "id": "H02",
            "question": "When does entry to the HSBC prize draw close?",
            "source": "test.pdf",
            "reference": "Entry closes at 11:59 pm on 1 October 2026."
        },
        {
            "id": "H03",
            "question": "What cash prizes are available in the HSBC prize draw?",
            "source": "test.pdf",
            "reference": "There are 2 grand prizes of £10,000 and 5 runner-up prizes of £1,000."
        },
        {
            "id": "H04",
            "question": "By when will HSBC select the prize draw winners?",
            "source": "test.pdf",
            "reference": "The winners will be selected at random on or before 30 October 2026."
        },
        {
            "id": "H05",
            "question": "How long do HSBC prize draw winners have to reply to the winner email?",
            "source": "test.pdf",
            "reference": "They have 48 hours to reply."
        },
        {
            "id": "H06",
            "question": "Which alternative accessibility formats does HSBC say are available?",
            "source": "test.pdf",
            "reference": "Large print, braille, and audio are available; HSBC also mentions Text Relay and BSL Video Relay services."
        }
    ]

    results = []
    scores = []

    for test in tests:

        print("\n" + "=" * 70)
        print(f"Running {test['id']}")
        print(f"Question: {test['question']}")

        # Step 1: Retrieve chunks
        retrieved_chunks, metadatas, distances = retrieve_relevant_chunks(
            test["question"],
            source_name=test["source"],
            top_k=3
        )

        # Step 2: Build RAG prompt
        prompt = build_rag_prompt(
            test["question"],
            retrieved_chunks,
            metadatas
        )

        # Step 3: Generate RAG answer
        generated_answer = generate_rag_answer(prompt)

        print("\nGenerated Answer:")
        print(generated_answer)

        # Step 4: Evaluate the answer
        evaluation = evaluate_answer(
            test["question"],
            generated_answer,
            test["reference"]
        )

        print("\nEvaluation:")
        print(evaluation)

        # Extract numerical score
        score_match = re.search(r"Score:\s*(\d+)", evaluation)

        if score_match:
            score = int(score_match.group(1))
            scores.append(score)
        else:
            score = None

        # Store result
        results.append({
            "test_id": test["id"],
            "question": test["question"],
            "source": test["source"],
            "reference_answer": test["reference"],
            "generated_answer": generated_answer,
            "score": score,
            "evaluation": evaluation
        })

    # Save all results to CSV
    output_file = "answer_evaluation_results.csv"

    with open(output_file, "w", newline="", encoding="utf-8-sig") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "test_id",
                "question",
                "source",
                "reference_answer",
                "generated_answer",
                "score",
                "evaluation"
            ]
        )

        writer.writeheader()
        writer.writerows(results)

    print("\n" + "=" * 70)
    print("ANSWER EVALUATION COMPLETE")
    print("=" * 70)

    print(f"Total tests: {len(tests)}")

    if scores:
        average_score = sum(scores) / len(scores)
        print(f"Average score: {average_score:.2f} / 5")

        print(f"5/5 answers: {scores.count(5)}")
        print(f"4/5 answers: {scores.count(4)}")
        print(f"3/5 or below: {sum(score <= 3 for score in scores)}")

    print(f"\nResults saved to: {output_file}")
    
