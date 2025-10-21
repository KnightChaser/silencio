# silencio

An LLM-based text redaction app for identifying and redacting sensitive information in documents. Uses OpenAI's structured output parsing to detect confidential items and Aho-Corasick algorithm for efficient pattern matching and replacement.

## Features

- **Automated Detection**: Leverages large language models to identify personally identifiable information (PII), company data, technical details, and confidential/legal information.
- **Structured Redaction**: Applies numbered redactions with policy codes and descriptions for traceability.
- **Interactive UI**: Built with Streamlit for easy text input and visualization of redacted content.
- **Efficient Processing**: Uses Aho-Corasick for fast, multi-pattern string matching.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/KnightChaser/silencio.git
   cd silencio
   ```

2. Install dependencies:

   ```bash
   uv sync
   ```

3. Set up your OpenAI API key:

   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```

## Usage

Run the Streamlit app:

```bash
uv run streamlit run app/streamlit_app.py
```

1. Paste your text into the input area.
2. Click "Run" to process the document.
3. View the highlighted sensitive items, redacted output, and detailed inventory table.

## Configuration

- **Model**: Set the OpenAI model via `MODEL_NAME` environment variable (default: `gpt-5-mini`).
- **API Key**: Required via `OPENAI_API_KEY` environment variable.

## Redaction Categories

The app detects and redacts items across four main categories:

1. **Personally Identifiable Information (PII)**: Names, contacts, identifiers, locations, etc.
2. **Company and Partner Information**: Corporate identities, projects, affiliates.
3. **Technical Details**: Credentials, configurations, code, logs, etc.
4. **Confidential and Legal Details**: Contracts, financial data, security info.

Each item is assigned a specific code (e.g., `(1)(A)(a)`) for precise classification.

## Warning

This tool provides automated assistance in identifying and redacting sensitive information, but it is not a (complete nor a perfect) substitute for human judgment. **Always** review and verify the redacted output manually to ensure complete protection of confidential data before use in any sensitive or legal context.
