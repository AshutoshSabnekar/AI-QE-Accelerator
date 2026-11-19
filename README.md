# AI-QE-Accelerator

An AI Quality Engineering portfolio project focused on building practical tools and techniques for evaluating the quality, reliability, and testability of software and AI-powered applications.

The project evolves incrementally through hands-on implementation, automated testing, experimentation, and documented engineering results.

## Objectives

- Build maintainable automated tests using Python and pytest.
- Develop reusable quality engineering utilities.
- Explore test optimization techniques such as Test Impact Analysis (TIA).
- Evaluate the quality and reliability of Large Language Model (LLM) applications.
- Test Retrieval-Augmented Generation (RAG) workflows and AI agents.
- Develop repeatable quality checks suitable for CI/CD pipelines.
- Document test strategies, evaluation results, and engineering trade-offs.

## Technology Stack

### Currently Implemented

- Python
- pytest
- Git and GitHub
- AST-based analysis
- pytest markers
- Test Impact Analysis

### Planned

- API testing tools
- LLM evaluation frameworks
- Prompt testing
- RAG evaluation
- AI agent testing
- CI/CD integration
- AI quality metrics and observability

Technologies will be introduced incrementally as the project develops.

## Project Structure

```text
AI-QE-Accelerator/
├── docs/
│   └── tia-implementation-report.md
├── src/
│   └── calculator.py
├── tests/
│   ├── test_addition.py
│   ├── test_factorial.py
│   └── test_math_operations.py
├── tools/
│   └── tia/
│       ├── __init__.py
│       ├── dependency_map.py
│       └── tia_runner.py
├── .github/
│   └── workflows/
│       └── python-tests.yml
├── .gitignore
├── README.md
├── pytest.ini
└── requirements.txt
