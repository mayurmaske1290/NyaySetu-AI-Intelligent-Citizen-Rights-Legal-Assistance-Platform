# Scripts

- `ingest_knowledge.py` — packs `knowledge_base/legal_sources/*.md` into JSON. Demo-only until you replace sources.
- `init_db.sql` — PostgreSQL + pgvector schema used by Docker Compose.
- `run_backend.ps1` — create venv, install, run uvicorn.

Replace demo markdown with verified extracts, then re-run ingest and reload the RAG store.
