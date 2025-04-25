from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl

class Settings(BaseSettings):
    API_COINGECKO: str
    API_COINGECKO_BASE_URL: AnyHttpUrl = "https://api.coingecko.com/api"
    FRONTEND_URL: AnyHttpUrl = "http://localhost:5173"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
