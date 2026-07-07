import os


class Settings:
    """Application settings loaded from environment variables."""

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./ecommerce.db")
    admin_secret_key: str = os.getenv("ADMIN_SECRET_KEY", "changeme")
    admin_username: str = os.getenv("ADMIN_USERNAME", "admin")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "admin")
    testing: bool = os.getenv("TESTING", "false").lower() == "true"


settings = Settings()
