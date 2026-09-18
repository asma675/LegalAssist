from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Rafi Legal Assist"
    environment: str = "development"
    database_url: str = "sqlite:///./rafi.db"
    secret_key: str = "change-me-in-production"
    access_token_minutes: int = 720
    openai_api_key: str | None = None
    openai_model: str = "gpt-5-mini"
    cors_origins: str = "http://localhost:5173,http://localhost:8080"
    upload_dir: str = "./uploads"
    max_upload_mb: int = 25
    demo_mode: bool = True
    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None
    stripe_price_professional: str | None = None
    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_redirect_uri: str = "http://localhost:8000/api/calendar/google/callback"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
