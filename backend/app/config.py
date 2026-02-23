from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "extra": "ignore"}

    database_url: str = "postgresql+asyncpg://ohhell:ohhell@localhost:5434/ohhell"
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/auth/google/callback"

    frontend_url: str = "http://localhost:5173"
    environment: str = "development"


settings = Settings()
