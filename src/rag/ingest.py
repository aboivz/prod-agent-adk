"""Document ingestion: load files → chunk text → embed → store in Qdrant."""

import hashlib
from pathlib import Path

from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

try:
    from agent.config import settings
except ModuleNotFoundError:
    from src.agent.config import settings


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks.

    Args:
        text: The input text to split.
        chunk_size: Maximum characters per chunk.
        overlap: Number of overlapping characters between consecutive chunks.

    Returns:
        List of text chunks.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return [c.strip() for c in chunks if c.strip()]


def load_documents(docs_dir: str = "docs") -> list[dict]:
    """Load all .md and .txt files, chunk them, return list of dicts."""
    docs = []
    for path in Path(docs_dir).glob("**/*"):
        if path.suffix in (".md", ".txt"):
            content = path.read_text(encoding="utf-8")
            chunks = chunk_text(
                content,
                chunk_size=settings.chunk_size,
                overlap=settings.chunk_overlap,
            )
            for i, chunk in enumerate(chunks):
                docs.append(
                    {
                        "id": hashlib.md5(f"{path.name}_{i}".encode()).hexdigest(),
                        "text": chunk,
                        "metadata": {
                            "source": path.name,
                            "chunk_index": i,
                        },
                    }
                )
    return docs


def ingest(docs_dir: str = "docs") -> int:
    """Full ingestion pipeline: load docs → embed → upsert to Qdrant.

    Returns:
        Number of chunks ingested.
    """
    client = QdrantClient(url=settings.qdrant_url)
    embed_model = TextEmbedding(model_name=settings.embedding_model)

    # Load & chunk documents
    documents = load_documents(docs_dir)
    if not documents:
        print("No documents found.")
        return 0

    texts = [doc["text"] for doc in documents]

    # Generate embeddings
    embeddings = list(embed_model.embed(texts))
    vector_size = len(embeddings[0])

    # Create collection (recreate if exists for clean ingestion)
    client.recreate_collection(
        collection_name=settings.qdrant_collection,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

    # Build and upsert points
    points = [
        PointStruct(
            id=idx,
            vector=embeddings[idx].tolist(),
            payload={"text": documents[idx]["text"], **documents[idx]["metadata"]},
        )
        for idx in range(len(documents))
    ]
    client.upsert(collection_name=settings.qdrant_collection, points=points)

    print(f"Ingested {len(points)} chunks into '{settings.qdrant_collection}'")
    return len(points)


if __name__ == "__main__":
    ingest()
