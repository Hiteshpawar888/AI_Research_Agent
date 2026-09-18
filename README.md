# AI Research & Knowledge Agent

An AI-powered research assistant that searches the web, gathers relevant information, and generates concise, structured research reports with citations and references.

## Overview

The **AI Research & Knowledge Agent** is designed to help users research a topic using current information from the web.

The system accepts a research question, validates the input, performs web research, and uses a Large Language Model (LLM) to generate a structured research report supported by sources.

The project is being developed step by step with a focus on:

- Reliable research
- Modular architecture
- Source-backed answers
- Cost-efficient API usage
- Explainable workflow
- Production-oriented development

## Current Workflow

```text
User Question
      ↓
Input Validation
      ↓
Research Agent
      ↓
Web Search
      ↓
Reliable Sources
      ↓
LLM Analysis
      ↓
Structured Research Report
      ↓
Citations & References
```

## Current Features

- Accepts research questions from users
- Validates user input
- Performs web-based research
- Uses an LLM to analyze retrieved information
- Generates concise research reports
- Supports citations for factual claims
- Provides references used during research
- Uses environment variables for API key protection
- Uses modular Python files
- Controls response length to reduce unnecessary API usage

## Report Structure

The generated research report contains:

1. Executive Summary
2. Key Findings
3. Analysis
4. Conclusion
5. References

## Project Structure

```text
AI-research-agent/
│
├── main.py
├── research_agent.py
├── requirements.txt
├── README.md
├── .gitignore
└── .env
```

### `main.py`

Handles the main application flow:

- Gets the research question
- Validates the input
- Calls the research agent
- Displays the final report

### `research_agent.py`

Handles the AI research functionality:

- Creates the AI client
- Builds the research prompt
- Uses web search
- Generates the structured research report

### `requirements.txt`

Contains the Python dependencies required by the project.

### `.env`

Stores sensitive environment variables such as the API key.

The `.env` file is excluded from Git using `.gitignore`.

## Technologies

- Python
- OpenAI API
- Web Search
- Large Language Models (LLMs)
- python-dotenv
- Git
- GitHub
- VS Code

## Installation

Clone the repository:

```bash
git clone https://github.com/Hiteshpawar888/AI_Research_Agent.git
```

Move into the project directory:

```bash
cd AI_Research_Agent
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Environment Setup

Create a `.env` file inside the project directory.

Add your API key:

```text
OPENAI_API_KEY=your_api_key_here
```

> Never commit or upload your real `.env` file or API key to GitHub.

## Run the Application

Run:

```bash
python main.py
```

Then enter a research question when prompted.

Example:

```text
What are the latest developments in Retrieval-Augmented Generation?
```

The agent will research the question and generate a structured report with citations and references.

## Example Output

```text
AI Research Report

1. Executive Summary
2. Key Findings
3. Analysis
4. Conclusion
5. References
```

## Future Improvements

The next stages of development will focus on:

- PDF and document research
- Retrieval-Augmented Generation (RAG)
- Vector database integration
- Multi-source research
- Agentic tool selection
- Source verification
- Retrieval and answer evaluation
- Better error handling
- Cost and latency monitoring
- Automated testing
- User-friendly interface
- Application deployment

## Security

Sensitive credentials are stored using environment variables.

The following files are excluded from Git:

```text
.env
__pycache__/
*.pyc
```

API keys should never be hard-coded into the Python source code.

## Project Status

🚧 **Under Active Development**

The current version supports web-based research and structured report generation. Additional RAG, agentic AI, evaluation, and deployment capabilities will be added progressively.

## Author

**Hitesh Pawar**

MSc Artificial Intelligence  
University of Southampton