from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    groq_api_key: str = ""
    database_url: str = "postgresql+asyncpg://marine_user:marine_password@localhost:5432/marine_db"
    copernicus_username: str = ""
    copernicus_password: str = ""
    
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
