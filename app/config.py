from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Configuration
    app_name: str
    debug: bool

    # Database Configuration
    database_url: str

    # Server Configuration
    host: str
    port: int

    # Authentication Configuration
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Create a global settings instance
settings = Settings()
