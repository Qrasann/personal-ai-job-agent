from __future__ import annotations

import re
from collections.abc import Sequence


MAX_REMOTE_QUERIES = 4

# These phrases identify plausible remote search roles, not individual vacancy
# work modes or permission to work from any country. Avoid generic words such
# as "customer", "engineer" or "operator" that also describe physical work.
_REMOTE_ROLES = re.compile(
    r"(?<!\w)(?:"
    r"customer (?:support|service)|technical support|it support|"
    r"help ?desk|service desk|data entry|"
    r"devops|devsecops|sre|sysadmin|"
    r"(?:systems?|linux|windows|network) administrator|"
    r"(?:infrastructure|platform|cloud|site reliability|software|support) engineer|"
    r"(?:software|backend|frontend|front end|full stack|web|python) developer|"
    r"служба поддержки|техническая поддержка|поддержка клиентов|техподдержка|"
    r"(?:оператор|специалист) поддержки|системный администратор|"
    r"(?:linux|сетевой) администратор|инженер инфраструктуры|ввод данных"
    r")(?!\w)"
)
_PHYSICAL_ROLES = re.compile(
    r"(?<!\w)(?:"
    r"warehouse|production (?:worker|operator)|factory|hotel staff|"
    r"kitchen|cleaner|construction|(?:delivery|truck|bus) driver|"
    r"cook|waiter|housekeep(?:er|ing)|forklift|picker|packer|barista|"
    r"склад(?:ской)?|кладовщик|уборщи(?:к|ца)|повар|кухонный|водитель|"
    r"строитель|курьер|грузчик|разнорабочий"
    r")(?!\w)"
)


def _query_key(query: str) -> str:
    normalized = re.sub(r"[‐‑‒–—-]+", " ", query.casefold().replace("ё", "е"))
    normalized = " ".join(normalized.split())
    return re.sub(r"\bhelp desk\b", "helpdesk", normalized)


def remote_discovery_queries(queries: Sequence[str] | None, *, limit: int = MAX_REMOTE_QUERIES) -> list[str]:
    """Plan a bounded remote-only search using the owner's selected queries.

    Remote-compatible roles receive earlier request slots so a later support
    query is not lost behind physical-work queries. The text and order of the
    first equivalent query are preserved within both groups; no role is added,
    excluded from preferences, or given a higher match score.
    """
    limit = min(MAX_REMOTE_QUERIES, max(0, limit))
    if not limit:
        return []
    remote: list[str] = []
    other: list[str] = []
    seen: set[str] = set()
    for query in queries or []:
        if not isinstance(query, str):
            continue
        text = query.strip()
        key = _query_key(text)
        if not key or key in seen:
            continue
        seen.add(key)
        group = remote if _REMOTE_ROLES.search(key) and not _PHYSICAL_ROLES.search(key) else other
        group.append(text)
    return (remote + other)[:limit]
