from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GENAI_API_KEY: str

    MONGO_URI: str
    DB_NAME: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()