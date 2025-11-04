"""Configuration for the Tree API."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # API settings
    api_title: str = "Tree Zipper API"
    api_version: str = "1.0.0"
    api_description: str = "FastAPI server implementing zipper-HATEOAS tree navigation"

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True

    # CORS settings
    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    class Config:
        """Pydantic configuration."""

        env_prefix = "TREE_API_"
        case_sensitive = False


# Global settings instance
settings = Settings()
