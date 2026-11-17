# Lab 2 — Kyiv Tourism Knowledge Extraction and GraphRAG

The project extracts structured facts from a corpus about Kyiv tourism, builds a vector index and a knowledge graph, detects Louvain communities, and compares vector-RAG with GraphRAG.

## Quick start

Run from the repository root:

```powershell
python -m pip install -r lab2/requirements.txt
python lab2/src/run_pipeline.py
python lab2/src/validate_lab2.py
python -m unittest discover -s lab2/tests -v
```

The default `offline` mode is deterministic and requires no API key. To demonstrate real LLM structured output, copy `.env.example` to `.env` and select either `gemini` or `ollama`. API keys must never be committed.

## Pipeline stages

1. Load and chunk eight text documents.
2. Extract typed facts into `data/facts.json`.
3. Create a reproducible 20-fact verification sample.
4. Build embeddings and compare keyword search with semantic search.
5. Build and visualize a NetworkX knowledge graph.
6. Detect Louvain communities and summarize each community.
7. Answer a global question with vector-RAG and GraphRAG.
8. Validate all measurable assignment requirements.

## Backends

- `offline`: curated extraction plus deterministic summaries; suitable for tests and demonstrations without network access.
- `gemini`: Gemini structured JSON output and optional Gemini embeddings.
- `ollama`: local LLM through Ollama's HTTP API.
- `sentence-transformers`: local pretrained embedding model after its first download.
- `hashing`: lightweight offline vector baseline with Ukrainian synonym normalization.

