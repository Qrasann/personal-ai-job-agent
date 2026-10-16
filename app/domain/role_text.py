"""Conservative role terms shared by discovery and fallback matching."""
from __future__ import annotations

import re


def role_tokens(text: str) -> set[str]:
    """Keep short names and distinguish Java/JavaScript and C/C++/C#."""
    return set(re.findall(r"\.?[^\W_]+(?:\+\+|#)?", text.casefold()))
