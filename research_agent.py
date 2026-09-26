import time

from openai import OpenAI
from config import get_api_key


client = OpenAI(api_key=get_api_key())


def generate_answer(question):
    """Search the web and generate a short research report."""

    prompt = f"""
Research this question using reliable web sources:

{question}

Create a concise professional research report with:

1. Executive Summary
2. Key Findings
3. Analysis
4. Conclusion
5. References

Requirements:
- Use only a few reliable sources.
- Cite important factual claims.
- Do not invent sources.
- Include only sources actually used.
- Keep the report concise.
- Maximum length: approximately 200 words.
"""

    try:
        response = client.responses.create(
            model="gpt-5.6-luna",
            reasoning={"effort": "none"},
            tools=[{"type": "web_search"}],
            tool_choice="required",
            input=prompt
        )

        return response.output_text

    except Exception as e:
        return f"Research failed: {e}"


def generate_rag_answer(prompt):
    """Generate a RAG answer and track API usage, cost, and response time."""

    try:
        start_time = time.time()

        response = client.responses.create(
            model="gpt-5.6-luna",
            reasoning={"effort": "none"},
            input=prompt
        )

        end_time = time.time()
        latency = end_time - start_time

        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        total_tokens = response.usage.total_tokens

        # Existing pricing values used by this project
        input_price_per_million = 0.20
        output_price_per_million = 1.20

        input_cost = (
            input_tokens / 1_000_000
        ) * input_price_per_million

        output_cost = (
            output_tokens / 1_000_000
        ) * output_price_per_million

        estimated_cost = input_cost + output_cost

        print("\n--- API Usage ---")
        print(f"Input tokens: {input_tokens}")
        print(f"Output tokens: {output_tokens}")
        print(f"Total tokens: {total_tokens}")
        print(f"Estimated cost: ${estimated_cost:.6f}")
        print(f"Response time: {latency:.2f} seconds")

        return response.output_text

    except Exception as e:
        return f"RAG research failed: {e}"


def verify_rag_answer(answer, relevant_chunks, metadatas):
    """Verify whether the RAG answer is supported by the retrieved sources."""

    context_parts = []

    for chunk, metadata in zip(relevant_chunks, metadatas):
        source = metadata.get("source", "Unknown source")
        page = metadata.get("page", "Unknown")

        context_parts.append(
            f"[Source: {source}, Page: {page}]\n{chunk}"
        )

    context = "\n\n".join(context_parts)

    verification_prompt = f"""
Verify whether the answer below is supported by the provided source context.

ANSWER:
{answer}

SOURCE CONTEXT:
{context}

Instructions:
- Use only the provided source context.
- Do not use outside knowledge.
- Check the factual claims in the answer.
- If all important claims are supported, return VERIFIED.
- If some claims are supported but others are not, return PARTIALLY VERIFIED.
- If important claims are unsupported or contradicted, return NOT VERIFIED.
- Briefly explain your decision.
- Clearly identify any unsupported claims.
- Keep the verification concise.
"""

    try:
        start_time = time.time()

        response = client.responses.create(
            model="gpt-5.6-luna",
            reasoning={"effort": "none"},
            input=verification_prompt
        )

        end_time = time.time()
        latency = end_time - start_time

        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        total_tokens = response.usage.total_tokens

        input_price_per_million = 0.20
        output_price_per_million = 1.20

        input_cost = (
            input_tokens / 1_000_000
        ) * input_price_per_million

        output_cost = (
            output_tokens / 1_000_000
        ) * output_price_per_million

        estimated_cost = input_cost + output_cost

        print("\n--- Verification API Usage ---")
        print(f"Input tokens: {input_tokens}")
        print(f"Output tokens: {output_tokens}")
        print(f"Total tokens: {total_tokens}")
        print(f"Estimated cost: ${estimated_cost:.6f}")
        print(f"Response time: {latency:.2f} seconds")

        return response.output_text

    except Exception as e:
        return f"Source verification failed: {e}"


def generate_combined_answer(prompt):
    """Generate an answer using PDF context together with web research."""

    try:
        start_time = time.time()

        enhanced_prompt = f"""
{prompt}

Additional response instructions:

- Keep the answer proportional to the user's question.
- For a short or simple question, answer in no more than 5 concise bullet points.
- Keep simple answers under about 180 words.
- Do not create more than 2 headings for a simple question.
- Do not add an executive summary or long conclusion unless explicitly requested.
- Do not list every possible detail if the question can be answered briefly.
- Use both PDF evidence and web evidence when relevant.
- Include only the most relevant PDF and web sources.
- Keep citations concise and clear.
"""

        response = client.responses.create(
            model="gpt-5.6-luna",
            reasoning={"effort": "none"},
            tools=[
                {
                    "type": "web_search",
                    "search_context_size": "low"
                }
            ],
            tool_choice="auto",
            input=enhanced_prompt
        )

        end_time = time.time()
        latency = end_time - start_time

        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        total_tokens = response.usage.total_tokens

        # Existing pricing values used by this project
        input_price_per_million = 0.20
        output_price_per_million = 1.20

        input_cost = (
            input_tokens / 1_000_000
        ) * input_price_per_million

        output_cost = (
            output_tokens / 1_000_000
        ) * output_price_per_million

        estimated_cost = input_cost + output_cost

        print("\n--- Combined Research API Usage ---")
        print(f"Input tokens: {input_tokens}")
        print(f"Output tokens: {output_tokens}")
        print(f"Total tokens: {total_tokens}")
        print(f"Estimated token cost: ${estimated_cost:.6f}")
        print(f"Response time: {latency:.2f} seconds")

        return response.output_text

    except Exception as e:
        return f"Combined research failed: {e}"