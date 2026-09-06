from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    telegram_bot_token: str = ""
    telegram_admin_chat_id: str = ""
    multi_user_registration: bool = False
    registration_invite_code: str = ""

    # HH vacancy discovery works without applicant OAuth, but anonymous access is
    # intentionally treated as a limited/captcha-prone source. New applicant API
    # registrations are not assumed to be available.
    hh_user_agent: str = "PersonalJobAgent/0.2 (contact@example.com)"
    hh_search_period_days: int = 2
    hh_public_per_page: int = 50
    hh_public_cache_minutes: int = 60
    hh_web_fallback_enabled: bool = True
    hh_web_max_pages: int = 3
    hh_web_user_agent: str = "Mozilla/5.0 (X11; Linux x86_64; rv:154.0) Gecko/20100101 Firefox/154.0"

    # Legacy/private applicant connector. Disabled by default. Keep this only for
    # accounts that already have legitimately issued applicant credentials.
    hh_private_api_enabled: bool = False
    hh_access_token: str = ""
    hh_resume_id: str = ""
    hh_chat_interval_minutes: int = 5

    search_interval_minutes: int = 15

    openai_api_key: str = ""
    openai_model: str = "gpt-5"

    auto_apply: bool = False
    auto_reply: bool = False
    auto_apply_min_score: int = 92
    auto_reply_min_confidence: float = 0.95

    database_url: str = "postgresql+asyncpg://jobagent:jobagent@postgres:5432/jobagent_v3"
    profile_path: Path = Path("data/profile.yaml")
    storage_path: Path = Path("/app/storage")


settings = Settings()
