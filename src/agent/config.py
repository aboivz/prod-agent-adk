from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    google_api_key: str
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "knowledge_base"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 3

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()