# AI Research & Knowledge Agent

An AI-powered research assistant that uses web search and a Large Language Model (LLM) to research user questions and generate concise, structured reports with citations and references.

## Project Overview

The AI Research & Knowledge Agent accepts a research question from the user, searches the web for relevant information, and uses an LLM to generate a structured research report.

The project is being developed step by step with a focus on modular design, reliable sources, cost-efficient API usage, and explainable outputs.

## Current Features

- Accepts research questions from the user
- Validates user input
- Uses an LLM for analysis and report generation
- Uses web search to retrieve current information
- Generates structured research reports
- Provides citations for important claims
- Provides a references section
- Uses environment variables to protect the API key
- Uses a modular Python project structure
- Controls report length to reduce unnecessary token usage

## Current Workflow

User Question
    ↓
Input Validation
    ↓
AI Research Agent
    ↓
Web Search
    ↓
Reliable Sources
    ↓
Analysis
    ↓
Structured Research Report
    ↓
Citations & References

## Project Structure

AI-research-agent/
│
├── main.py
├── research_agent.py
├── requirements.txt
├── .env
└── README.md

## Technologies Used

- Python
- OpenAI API
- OpenAI Web Search
- python-dotenv
- VS Code

## Installation

Install the required Python packages:

pip install -r requirements.txt

## Environment Setup

Create a `.env` file in the project directory and add your API key:

OPENAI_API_KEY=your_api_key_here

Never upload your real API key to GitHub.

## Running the Project

Run the application using:

python main.py

Then enter a research question when prompted.

Example:

What are the latest developments in Retrieval-Augmented Generation?

## Example Output Structure

1. Executive Summary
2. Key Findings
3. Analysis
4. Conclusion
5. References

## Future Improvements

The project will be extended with:

- Document and PDF research
- Retrieval-Augmented Generation (RAG)
- Multi-source research
- Agentic decision-making
- Source verification
- RAG and answer evaluation
- Error handling
- Cost and latency monitoring
- User-friendly interface
- Deployment
- Automated testing

## Project Status

Currently under active development.