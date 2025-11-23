from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    abuseipdb_api_key: str
    virustotal_api_key: str
    abuse_confidence_score_threshold: int = 50
    max_age_in_days: int = 90

    class Config:
        env_file = "backend/.env"

settings = Settings()
