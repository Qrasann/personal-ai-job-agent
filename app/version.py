from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def current_version() -> str:
    try:
        return Path("VERSION").read_text(encoding="utf-8").strip() or "dev"
    except OSError:
        return "dev"
