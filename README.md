# AI Code Vault

AI Code Vault is a **Secure Agentic RAG system** built with Streamlit for the BSAI 4th Semester project.

The platform is designed to ingest user files, build searchable knowledge representations, and answer questions with transparent, context-aware, and secure AI workflows.

## Core Idea

AI Code Vault combines:
- A Streamlit web interface for user interaction
- A file ingestion and processing pipeline
- Embedding-based retrieval with semantic search
- Agentic orchestration for multi-step reasoning and actions
- Secure configuration via environment variables
- MySQL-backed persistence for metadata and audit-friendly records

## Project Checklist Coverage (11 Categories)

Below is how AI Code Vault satisfies the required checklist categories.

1. **User System**
   - Supports user-focused interaction through a clean Streamlit interface.
   - Separates user actions (upload, search, ask, manage) into clear workflows.

2. **File Pipeline**
   - Accepts files for ingestion.
   - Applies parsing, chunking, and preprocessing for retrieval-ready data.

3. **Agentic AI**
   - Uses an agent-style flow to decide retrieval steps, context assembly, and response generation.
   - Supports task decomposition for multi-step query handling.

4. **Smart Search**
   - Implements semantic search using sentence-transformer embeddings.
   - Retrieves relevant chunks beyond exact keyword matching.

5. **RAG Architecture**
   - Uses retrieval-augmented generation: retrieve context first, then generate answers.
   - Grounds responses on indexed project data to reduce hallucinations.

6. **Data Storage / Database**
   - Uses MySQL for structured data (users, document metadata, logs, or indexing references).
   - Enables persistence and lifecycle management of project records.

7. **Security and Access Control**
   - Stores secrets using environment variables (not hardcoded).
   - Supports safe credential handling for Groq and MySQL.

8. **AI Integration (LLM Provider)**
   - Integrates Groq API for fast inference and LLM response generation.
   - Keeps model integration modular for future provider upgrades.

9. **Visualization and Insights**
   - Uses pandas and matplotlib to generate analytics views (usage, retrieval quality, upload stats).
   - Provides interpretable outputs for users and evaluators.

10. **Frontend / Usability**
   - Delivers an interactive Streamlit dashboard.
   - Focuses on clear navigation for upload, query, and result inspection.

11. **Deployment and Reproducibility**
   - Ready for GitHub Codespaces setup with dependency-managed environment.
   - Includes explicit requirements and env template for consistent team setup.

## Tech Stack

- Streamlit
- pandas
- matplotlib
- groq
- sentence-transformers
- mysql-connector-python

## Environment Variables

Create a `.env` file with the required keys:

- `GROQ_API_KEY`
- `MYSQL_HOST`
- `MYSQL_PORT`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_DATABASE`

A starter template is included in the project.

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure environment variables in `.env`.
3. Run the app:
   ```bash
   streamlit run main.py
   ```

## Project Goal

Deliver a secure, explainable, and scalable AI document assistant that demonstrates end-to-end **Agentic RAG** capabilities for academic and practical evaluation.
