"""
Centralized application configuration.

All values are overridable via environment variables (see .env.example).
Keeping configuration in one place makes it obvious what's tunable when
running locally vs. in Docker Compose.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    app_name: str = "ecommerce-backend"
    environment: str = "local"

    # --- Database ---
    database_url: str = "sqlite:///./ecommerce.db"

    # --- CORS ---
    cors_allow_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # --- OpenTelemetry ---
    otel_enabled: bool = True
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"
    otel_service_name: str = "ecommerce-backend"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allow_origins.split(",") if origin.strip()]


settings = Settings()
