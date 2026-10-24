from __future__ import annotations

import difflib
import hashlib


MAX_RESUME_TEXT_CHARS = 100_000


def content_digest(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def validate_resume_edit(original: str, proposed: str) -> str:
    proposed = proposed.strip()
    if not proposed:
        raise ValueError("Новый текст CV не может быть пустым.")
    if len(proposed) > MAX_RESUME_TEXT_CHARS:
        raise ValueError("Текст CV превышает лимит 100 000 символов.")
    if proposed == original.strip():
        raise ValueError("Новый текст совпадает с текущей версией CV.")
    return proposed


def render_resume_text_diff(original: str, proposed: str, *, limit: int = 3200) -> str:
    lines = difflib.unified_diff(
        original.splitlines(), proposed.splitlines(),
        fromfile="approved/current", tofile="proposed/draft", lineterm="",
    )
    rendered = "\n".join(lines)
    if len(rendered) <= limit:
        return rendered
    return rendered[: max(0, limit - 30)].rstrip() + "\n… diff truncated …"
