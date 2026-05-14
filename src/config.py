from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "rag_ollama_chroma"

    EMBED_MODEL: str = "embeddinggemma"
    LLM_MODEL: str = "gemma3"

    COLLECTION_NAME: str = "company_knowledge_base"

    CHUNK_SIZE_WORDS: int = 180
    CHUNK_OVERLAP_WORDS: int = 35

    VECTOR_TOP_K: int = 6
    HYBRID_CANDIDATES: int = 12
    FINAL_TOP_K: int = 5
    RERANK_TOP_N: int = 8

    VECTOR_WEIGHT: float = 0.60
    BM25_WEIGHT: float = 0.40

    DATA_RAW_DIR: Path = Field(default=ROOT_DIR / "data" / "raw")
    CHROMA_DIR: Path = Field(default=ROOT_DIR / "chroma_db")
    REPORTS_DIR: Path = Field(default=ROOT_DIR / "reports")
    EVAL_DIR: Path = Field(default=ROOT_DIR / "eval")


settings = Settings()