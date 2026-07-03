"""Application settings with Pydantic validation."""

from functools import lru_cache
from typing import List, Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized application configuration.
    
    Uses Pydantic Settings for:
    - Environment variable loading
    - Type validation
    - Default values
    - .env file support
    
    Singleton pattern via lru_cache ensures single instance.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Environment
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment"
    )
    debug: bool = Field(default=False, description="Debug mode")
    
    # API Configuration
    host: str = Field(default="0.0.0.0", description="API host")
    port: int = Field(default=8000, ge=1, le=65535, description="API port")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )
    cors_origins: List[str] = Field(
        default=["*"],
        description="CORS allowed origins"
    )
    
    # LLM Configuration
    llm_provider: Literal["openai", "gemini", "groq"] = Field(
        default="openai",
        description="LLM provider"
    )
    openai_api_key: str = Field(default="", description="OpenAI API key")
    gemini_api_key: str = Field(default="", description="Gemini API key")
    groq_api_key: str = Field(default="", description="Groq API key")
    llm_model: str = Field(default="gpt-4", description="LLM model name")
    llm_temperature: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        description="LLM temperature"
    )
    llm_max_tokens: int = Field(
        default=2000,
        ge=1,
        description="LLM max tokens"
    )
    llm_timeout: int = Field(
        default=30,
        ge=1,
        description="LLM timeout in seconds"
    )
    
    # Embedding Configuration
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Embedding model"
    )
    embedding_dimension: int = Field(
        default=384,
        ge=1,
        description="Embedding dimension"
    )
    
    # Vector Store Configuration
    chroma_persist_directory: str = Field(
        default="./data/embeddings",
        description="ChromaDB persist directory"
    )
    chroma_collection_name: str = Field(
        default="shl_assessments",
        description="ChromaDB collection name"
    )
    
    # Catalog Configuration
    catalog_path: str = Field(
        default="./data/processed/catalog.json",
        description="Catalog JSON path"
    )
    catalog_url: str = Field(
        default="https://www.shl.com/solutions/products/product-catalog/",
        description="SHL catalog URL"
    )
    
    # Retrieval Configuration
    retrieval_top_k: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Top K retrieval results"
    )
    retrieval_similarity_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Similarity threshold"
    )
    
    # Conversation Configuration
    max_conversation_turns: int = Field(
        default=8,
        ge=1,
        le=20,
        description="Maximum conversation turns"
    )
    conversation_timeout: int = Field(
        default=30,
        ge=1,
        le=120,
        description="Conversation timeout in seconds"
    )
    
    # Recommendation Configuration
    max_recommendations: int = Field(
        default=10,
        ge=1,
        le=10,
        description="Maximum recommendations to return"
    )
    min_recommendations: int = Field(
        default=1,
        ge=1,
        description="Minimum recommendations to return"
    )
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == "development"


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses lru_cache to ensure singleton pattern.
    Settings are loaded once and reused throughout application lifecycle.
    """
    return Settings()
