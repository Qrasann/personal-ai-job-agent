from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    telegram_bot_token: str = ""
    telegram_admin_chat_id: str = ""
    multi_user_registration: bool = False
    registration_invite_code: str = ""

    hh_access_token: str = ""
    hh_resume_id: str = ""
    hh_user_agent: str = "JobAgentV3/0.1 (contact@example.com)"
    hh_search_period_days: int = 2
    search_interval_minutes: int = 15
    hh_chat_interval_minutes: int = 5

    openai_api_key: str = ""
    openai_model: str = "gpt-5"

    auto_apply: bool = False
    auto_reply: bool = False
    auto_apply_min_score: int = 92
    auto_reply_min_confidence: float = 0.95

    database_url: str = "postgresql+asyncpg://jobagent:jobagent@postgres:5432/jobagent_v3"
    profile_path: Path = Path("data/profile.yaml")


settings = Settings()
