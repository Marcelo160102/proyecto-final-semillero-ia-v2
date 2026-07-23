from pydantic_settings import BaseSettings
from functools import lru_cache


class Config(BaseSettings):
    google_api_key: str = ""
    gemini_model: str = "gemini-3.1-flash-lite"
    embedding_model: str = "gemini-embedding-2-preview"
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    database_url: str = "sqlite+aiosqlite:///./solicitudes.db"
    phoenix_host: str = "localhost"
    phoenix_port: int = 6006

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def obtener_config() -> Config:
    return Config()
