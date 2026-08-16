import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Configuration
    APP_TITLE: str = "TicketDesk API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", alias="ENVIRONMENT")
    PORT: int = Field(default=8000, alias="PORT")

    # Database Settings - Individual Parameters
    DB_HOST: Optional[str] = Field(default=None, alias="DB_HOST")
    DB_PORT: Optional[int] = Field(default=5432, alias="DB_PORT")
    DB_NAME: Optional[str] = Field(default=None, alias="DB_NAME")
    DB_USER: Optional[str] = Field(default=None, alias="DB_USER")
    DB_PASSWORD: Optional[str] = Field(default=None, alias="DB_PASSWORD")

    # Database Settings - Direct URL Override
    DATABASE_URL: Optional[str] = Field(default=None, alias="DATABASE_URL")

    # AWS S3 Settings
    AWS_REGION: str = Field(default="ap-southeast-1", alias="AWS_REGION")
    AWS_S3_BUCKET_NAME: Optional[str] = Field(default=None, alias="AWS_S3_BUCKET_NAME")
    ATTACHMENTS_BUCKET: Optional[str] = Field(default=None, alias="ATTACHMENTS_BUCKET")
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, alias="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, alias="AWS_SECRET_ACCESS_KEY")

    # CORS Configuration
    ALLOWED_ORIGINS: str = Field(default="*", alias="ALLOWED_ORIGINS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def s3_bucket_name(self) -> str:
        """
        Returns resolved S3 bucket name checking ATTACHMENTS_BUCKET first, then AWS_S3_BUCKET_NAME.
        """
        return self.ATTACHMENTS_BUCKET or self.AWS_S3_BUCKET_NAME or "ticketdesk-attachments"

    @property
    def database_uri(self) -> str:
        """
        Returns the resolved database connection URI.
        If DATABASE_URL is explicitly set, it takes precedence.
        Otherwise, builds a PostgreSQL URL from individual parameters.
        If neither are provided, defaults to SQLite for easy local development.
        """
        if self.DATABASE_URL:
            return self.DATABASE_URL

        if self.DB_HOST and self.DB_USER and self.DB_NAME:
            pwd = f":{self.DB_PASSWORD}" if self.DB_PASSWORD else ""
            port = f":{self.DB_PORT}" if self.DB_PORT else ""
            return f"postgresql://{self.DB_USER}{pwd}@{self.DB_HOST}{port}/{self.DB_NAME}"

        # Fallback to local SQLite DB if no postgres params provided
        return "sqlite:///./ticketdesk.db"

    @property
    def cors_origins(self) -> List[str]:
        """
        Parses ALLOWED_ORIGINS string into a list of origins for FastAPI CORSMiddleware.
        """
        if not self.ALLOWED_ORIGINS or self.ALLOWED_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


settings = Settings()
