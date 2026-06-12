from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    gemini_api_key: str = ""
    database_url: str = ""
    indb_file_path: str = "./data/Anuvaad_INDB_2024.11.xlsx"
    upload_dir: str = "./uploads"
    secret_key: str = "change-me-in-production"
    cors_origins: List[str] = ["http://localhost:3000"]
    max_upload_size_mb: int = 10
    razorpay_key_id: str = ""
    razorpay_key_secret: str = "dev_secret"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
