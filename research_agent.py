import os
from openai import OpenAI


# Create OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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

    response = client.responses.create(
        model="gpt-5.6-luna",
        reasoning={"effort": "none"},
        tools=[{"type": "web_search"}],
        input=prompt
    )

    return response.output_text