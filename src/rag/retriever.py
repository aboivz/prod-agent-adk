"""Retrieve relevant chunks from Qdrant vector database."""

from fastembed import TextEmbedding
from qdrant_client import QdrantClient

try:
    from agent.config import settings
except ModuleNotFoundError:
    from src.agent.config import settings

# Initialize once at module level (singleton pattern - tránh khởi tạo lại mỗi request)
_client = QdrantClient(url=settings.qdrant_url)
_embed_model = TextEmbedding(model_name=settings.embedding_model)


def search_knowledge(query: str, top_k: int | None = None) -> list[dict]:
    """Search Qdrant for chunks most relevant to the query.

    Args:
        query: Natural language search query.
        top_k: Number of results to return. Defaults to settings.top_k.

    Returns:
        List of dicts with keys: text, source, score.
    """
    top_k = top_k or settings.top_k

    # Embed the query using same model as ingestion
    query_embedding = list(_embed_model.embed([query]))[0].tolist()

    # Search Qdrant
    results = _client.query_points(
        collection_name=settings.qdrant_collection,
        query=query_embedding,
        limit=top_k,
    ).points

    return [
        {
            "text": point.payload["text"],
            "source": point.payload.get("source", "unknown"),
            "score": point.score,
        }
        for point in results
    ]
