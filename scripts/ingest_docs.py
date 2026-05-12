"""CLI script to ingest documents into Qdrant.

Usage: uv run python -m scripts.ingest_docs
"""

from src.rag.ingest import ingest

if __name__ == "__main__":
    count = ingest()
    print(f"Done. Total chunks: {count}")