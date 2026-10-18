from __future__ import annotations

import html


def manual_source_line(item) -> str:
    """Render a link-only source without suggesting the bot scans it."""
    name = html.escape(item.name)
    if item.url:
        name = f'<a href="{html.escape(item.url, quote=True)}">{name}</a>'
    note = f" · {html.escape(item.availability_note)}" if item.availability_note else ""
    return f"🔗 {name} — {html.escape(item.scope)} — ручной поиск{note}"
