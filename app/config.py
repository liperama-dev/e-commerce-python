import os


class Settings:
    """Application settings loaded from environment variables."""

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./ecommerce.db")
    admin_secret_key: str = os.getenv("ADMIN_SECRET_KEY", "changeme")


settings = Settings()
