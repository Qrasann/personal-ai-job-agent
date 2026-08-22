from functools import lru_cache
from pathlib import Path
import yaml

from app.config import settings


@lru_cache(maxsize=1)
def load_profile(path: Path | None = None) -> dict:
    profile_path = path or settings.profile_path
    with open(profile_path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)
