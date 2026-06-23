# src/config/settings.py
from functools import cached_property
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # --- Gemini ---
    google_api_key: str = Field(..., validation_alias="gemini_api_key")
    gemini_model: str = Field(default="gemini-2.5-flash", validation_alias="gemini_model")

    # --- Groq ---
    groq_api_key: str = Field(..., validation_alias="groq_api_key")
    groq_model: str = Field(default="llama-3.3-70b-versatile", validation_alias="groq_model")

    # --- OpenAI / Compatible ---
    openai_api_key: str = Field(..., validation_alias="openai_api_key")
    openai_base_url: str = Field(
        default="https://api.openai.com/v1",
        validation_alias="openai_base_url"
    )
    openai_model: str = Field(default="gpt-4o-mini", validation_alias="openai_model")

    # --- Common Settings ---
    dry_run: bool = Field(default=True, validation_alias="cloudops_buddy_dry_run")
    log_level: str = Field(default="INFO", validation_alias="cloudops_buddy_log_level")
    allowed_commands_str: str = Field(
        default="aws,az,kubectl,terraform,docker,ping,curl",
        validation_alias="cloudops_buddy_allowed_commands"
    )
    command_timeout: int = Field(default=30, validation_alias="cloudops_buddy_command_timeout")
    max_iterations: int = 3  # reserved for future use

    @field_validator("allowed_commands_str")
    @classmethod
    def validate_allowed_commands(cls, v: str) -> str:
        items = [item.strip() for item in v.split(",") if item.strip()]
        return ",".join(items) if items else "aws,kubectl,terraform,docker,ping,curl,az"

    @cached_property
    def allowed_commands(self) -> list[str]:
        """Return a list of allowed commands from the comma‑separated string."""
        return [item.strip() for item in self.allowed_commands_str.split(",") if item.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

settings = Settings()