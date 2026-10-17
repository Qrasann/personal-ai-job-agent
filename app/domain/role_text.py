"""Conservative role terms shared by discovery and fallback matching."""
from __future__ import annotations

import re


def role_tokens(text: str) -> set[str]:
    """Keep short names and normalize the common system/systems role variant."""
    tokens = set(re.findall(r"\.?[^\W_]+(?:\+\+|#)?", text.casefold()))
    if "systems" in tokens:
        tokens.remove("systems")
        tokens.add("system")
    return tokens
