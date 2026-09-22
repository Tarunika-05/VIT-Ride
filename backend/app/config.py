import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    GOOGLE_MAPS_API_KEY: str = ""
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
    VIT_CAMPUS_LAT: float = 12.840658
    VIT_CAMPUS_LON: float = 80.153187
    DEFAULT_GEMINI_MODEL: str = "gemini-3.6-flash"

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
