# Contract Clause Extractor

Extracts clauses and contract metadata from PDF documents using an LLM, stores them in SQLite, and exposes a FastAPI API to submit documents and query extractions.

## Setup Instructions

- Prerequisites

  - Python 3.9+
  - `uvicorn`, `fastapi`, `pydantic`, `aiosqlite`, `python-multipart`, `dotenv`, `openai`, `pypdf` (installed via `requirements.txt`)

- Local run

  1. Create and activate a virtual environment
     - Windows: `python -m venv .venv && .venv\\Scripts\\activate`
     - Unix/macOS: `python -m venv .venv && source .venv/bin/activate`
  2. Install dependencies: `pip install -r requirements.txt`
  3. Create `.env` in project root and set
     - `DB_PATH=./data.db` (or any writable path to your SQLite file)
     - `DEEPSEEK_API_KEY=<your_api_key>`
  4. Start the server: `uvicorn main:app --reload --port 8001`
  5. API base: `http://localhost:8001`

- Docker run

  1. Build: `docker build -t contract-clause-extractor .`
  2. Run: `docker run -e DB_PATH=data.db -e DEEPSEEK_API_KEY=<your_api_key> -p 80:80 contract-clause-extractor`
  3. API base: `http://localhost`

- Database initialization
  - On application startup, `create_database()` runs and creates tables and indexes if needed.

## Demo

- End-to-end script
  - Run the API locally: `uvicorn main:app --reload --port 8001`
  - Execute demo: `python demo_e2e.py path/to/sample.pdf --api http://localhost:8001`
  - The script uploads the PDF, prints the extracted payload, lists extractions, and fetches extractions by the first returned `document_id`.

- Docker
  - Start container: `docker run -e DB_PATH=data.db -e DEEPSEEK_API_KEY=<your_api_key> -p 8080:80 contract-clause-extractor`
  - Execute demo against container: `python demo_e2e.py path/to/sample.pdf --api http://localhost:8080`

## API Overview

- `POST /api/extract`

  - Accepts a PDF upload `multipart/form-data` with field `document`
  - Returns the extracted JSON payload and persists it
  - Example:
    - `curl -X POST -F "document=@sample.pdf" http://localhost:8001/api/extract`

- `GET /api/extractions?pageNum=<n>&pageSize=<m>`

  - Lists extractions in pages

- `GET /api/extractions/{document_id}`
  - Lists extractions associated with a specific `document_id`

## Design Decisions and Tradeoffs

- Pydantic v2 models for validation

  - Validators normalize and enforce basic constraints (e.g., non-empty names, trimming strings, clause ordering).
  - DB constraints are kept minimal; validation happens at the model layer.

- Repository + Service layers

  - Repositories encapsulate raw SQL for each entity.
  - The service layer composes repository calls (e.g., save document, extraction, clauses, and metadata in sequence), keeping routers thin and testable.
  - Tradeoff: Slightly more code and indirection, but clearer separation of concerns and easier unit testing.

- SQLite with `aiosqlite`

  - Simplicity and portability for local/dev usage; async interface fits FastAPI.
  - Tradeoff: No connection pooling; each repository call opens a connection for clarity and isolation.

- Metadata `parties` stored as JSON in `TEXT`

  - Flexible representation avoids CSV parsing issues.
  - Tradeoff: No SQL-level normalization of parties; relies on application logic.

- PDF text extraction via `pypdf`

  - Lightweight and simple; extracts contiguous text from pages.
  - Tradeoff: Complex layouts or scanned PDFs may require OCR or advanced parsing, which is out of scope.

- LLM integration
  - `openai` client pointing to DeepSeek with `response_format={"type":"json_object"}` for strict JSON.
  - Tradeoff: External dependency; robust error handling added for provider errors.

## What I’d Improve With More Time

- Query performance and richer schema

  - Add more indexes (e.g., clause name, range-based queries on `start/end`).
  - Consider additional `CHECK` constraints or normalization for metadata fields.

- Robust PDF processing

  - Improve text extraction for complex or scanned documents (OCR).

- Reading Different File Types

  - Add support for non-PDF file types (e.g., docx, txt) by extracting text.

  - Validate schema strictly before persisting; add retries and guardrails.
  - Add rate limiting and observability (logging/metrics) for LLM calls.

- Testing and CI

  - Unit tests for services and repositories.
  - Contract tests for routers; add lint/type-check steps in CI.

- Configuration and ops
  - Switch to PostgreSQL in production with an async driver and migrations.

## Project Structure

- `main.py` sets up FastAPI and runs DB initialization in lifespan.
- `routers/` contains HTTP endpoints (`extract`, `extractions`).
- `services/` contains orchestration over repositories (`extraction_service`).
- `repositories/` contains per-entity DB operations.
- `models/` contains Pydantic models and validators.
- `database.py` contains DB path resolution and schema creation.
- `openai_client.py` contains DeepSeek call logic.

## Architecture Diagram

```
+----------------+           +-------------------------------+
|    Client      |  POST     |   FastAPI Router: /api/extract |
| (Browser/CLI)  |---------> | - Validate PDF upload          |
|                |           | - Read PDF via pypdf           |
|                |           | - Call LLM (DeepSeek)          |
|                |           | - Pass payload to Service      |
+----------------+           +---------------+----------------+
                                                |
                                                v
                                   +---------------------------+
                                   |  Service Layer            |
                                   |  save_extraction          |
                                   |  - insert document        |
                                   |  - insert extraction      |
                                   |  - insert clauses (bulk)  |
                                   |  - insert metadata        |
                                   +---------------+-----------+
                                                   |
                                                   v
                              +------------------------------+
                              |        Repository Layer       |
                              |  document/extraction/clause/  |
                              |  metadata repositories        |
                              +---------------+--------------+
                                              |
                                              v
                                  +---------------------+
                                  |      SQLite DB      |
                                  |  via aiosqlite      |
                                  +---------------------+


Retrieval:

Client GET /api/extractions/{document_id} or /api/extractions?pageNum=&pageSize=
    -> FastAPI Router
        -> Service (get_by_document_id / list_extractions)
            -> Repositories (query extraction + clauses + metadata)
                -> Compose Pydantic models and return JSON

Startup:
    FastAPI lifespan -> `create_database()` -> ensure tables/indexes exist

Config:
    `.env` or container env
      - `DB_PATH` (SQLite file path)
      - `DEEPSEEK_API_KEY` (DeepSeek API key)
```
