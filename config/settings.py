import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field


load_dotenv()       

class Settings(BaseSettings):
    telegram_bot_token: str = Field(..., validation_alias="TELEGRAM_BOT_TOKEN") 
    gemini_api_key: str = Field(..., validation_alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.5-flash", validation_alias="GEMINI_MODEL")    
    vera_api_url: str = Field(..., validation_alias="VERA_API_URL")
    vera_api_key: str = Field(..., validation_alias="VERA_API_KEY")
    
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    max_file_size_mb: int = Field(default=20, validation_alias="MAX_FILE_SIZE_MB")
    temp_download_path: Path = Field(default=Path("./temp_downloads"), validation_alias="TEMP_DOWNLOAD_PATH")
    
    gemini_timeout: int = 120
    vera_timeout: int = 60
    max_image_size_mb: int = 10
    max_video_size_mb: int = 50
    max_audio_size_mb: int = 20
    
    accepted_image_formats: list = ["image/jpeg", "image/png", "image/webp"]
    accepted_video_formats: list = ["video/mpeg", "video/mp4"]
    accepted_audio_formats: list = ["audio/mpeg", "audio/ogg", "audio/wav"]
    
    model_config = {"env_file": ".env", "case_sensitive": False}
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.temp_download_path.mkdir(parents=True, exist_ok=True)
    
    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

settings = Settings()

# Configurer le logger APRÈS settings
from utils.logger import setup_logger
logger = setup_logger(log_level=settings.log_level)