from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "change-this-in-production-secret-key-32-bytes-min"
    ALLOWED_ORIGINS: list[str] = []

    # PostgreSQL Database
    DATABASE_URL: str = (
        "postgresql+asyncpg://ikg_user:ikg_password@localhost:5432/ikg_db"
    )
    ALEMBIC_DATABASE_URL: str = (
        "postgresql+psycopg://ikg_user:ikg_password@localhost:5432/ikg_db"
    )
    DATABASE_SSL: str = "disable"  # "require", "verify-full", or "disable"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    # Optional / Future Roadmap: Neo4j Graph Database (Release 1.0)
    # v0.1 stores relationships in PostgreSQL; Neo4j is not wired to runtime
    NEO4J_URI: str | None = None
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "ikg_password"

    # Optional / Future Roadmap: Qdrant Vector Database (v0.1 uses in-process embeddings; Beta 0.5 uses pgvector)
    QDRANT_URL: str | None = None

    # Redis Cache & Task Queue
    REDIS_URL: str = "redis://localhost:6379/0"

    # MinIO Object Storage
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "ikg-evidence"

    # AI & LLM Settings
    LLM_PROVIDER: Literal["gemini", "ollama"] = "gemini"
    GEMINI_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3:8b"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
