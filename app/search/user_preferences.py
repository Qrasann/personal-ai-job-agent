from __future__ import annotations

import re
import shlex
from datetime import UTC, datetime, timedelta

from app.domain.blacklist import BLACKLIST_RULE_KINDS


SALARY_KINDS = {"current", "desired", "minimum"}
_CURRENCY = re.compile(r"^[A-Z]{3}$")


def parse_salary_command(text: str) -> tuple[str, str, int | None]:
    """Parse `/salary <kind> <currency> <amount|clear>` into a safe update."""
    parts = text.split()
    if len(parts) != 4 or parts[1].casefold() not in SALARY_KINDS:
        raise ValueError("Формат: /salary current|desired|minimum USD 3000 (или clear)")
    kind, currency, amount_text = parts[1].casefold(), parts[2].upper(), parts[3].casefold()
    if not _CURRENCY.fullmatch(currency):
        raise ValueError("Укажи код валюты из трёх букв, например RUB, USD или EUR.")
    if amount_text == "clear":
        return kind, currency, None
    if not amount_text.isdecimal() or not 0 < int(amount_text) <= 100_000_000:
        raise ValueError("Сумма должна быть целым числом от 1 до 100 000 000.")
    return kind, currency, int(amount_text)


def update_salary(settings: dict, kind: str, currency: str, amount: int | None) -> dict:
    result = dict(settings)
    values = dict(result.get(f"{kind}_salary") or {})
    if amount is None:
        values.pop(currency, None)
    else:
        values[currency] = amount
    result[f"{kind}_salary"] = values
    if kind == "minimum":
        minimum = dict(result.get("minimum_salary") or {})
        if amount is None:
            minimum.pop(currency, None)
        else:
            minimum[currency] = amount
        result["minimum_salary"] = minimum
    return result


def update_blacklist(settings: dict, action: str, term: str = "") -> dict:
    result = dict(settings)
    terms = [str(item).strip() for item in result.get("exclude_terms", []) if str(item).strip()]
    if action == "undo":
        previous = result.pop("_blacklist_undo", None)
        if isinstance(previous, list):
            result["exclude_terms"] = [str(item).strip() for item in previous if str(item).strip()]
        return result
    if action not in {"add", "remove", "clear"}:
        raise ValueError("Действие blacklist должно быть add, remove, clear или undo.")
    result["_blacklist_undo"] = list(terms)
    if action == "add" and term.strip():
        if term.strip().casefold() in {"betting", "gambling", "букмек", "букмекер", "казино", "casino", "igaming", "crypto casino", "crypto", "web3", "blockchain"}:
            raise ValueError("Отраслевые предпочтения настраиваются через /employerpolicy category <категория> allow|warn|block.")
        if not any(item.casefold() == term.strip().casefold() for item in terms):
            terms.append(term.strip())
    elif action == "remove":
        terms = [item for item in terms if item.casefold() != term.strip().casefold()]
    elif action == "clear":
        terms = []
    result["exclude_terms"] = terms
    return result


def preview_blacklist(settings: dict, action: str, term: str = "") -> dict:
    """Return a before/after preview without mutating persisted preferences."""
    current = [str(item).strip() for item in (settings.get("exclude_terms") or []) if str(item).strip()]
    preview_settings = dict(settings)
    if action == "undo":
        previous = preview_settings.get("_blacklist_undo")
        after = [str(item).strip() for item in previous if str(item).strip()] if isinstance(previous, list) else current
    else:
        after = update_blacklist(preview_settings, action, term).get("exclude_terms", current)
    return {"action": action, "term": term.strip(), "before": current, "after": list(after)}


def parse_blacklist_rule_command(text: str) -> dict:
    """Parse the structured `/blacklist rule ...` command without side effects."""
    try:
        parts = shlex.split(text)
    except ValueError as exc:
        raise ValueError("Проверь кавычки в команде blacklist.") from exc
    if len(parts) < 3 or parts[1].casefold() != "rule":
        raise ValueError("Формат: /blacklist rule preview add company <название> [--profile all] [--until YYYY-MM-DD]")
    preview = parts[2].casefold() == "preview"
    action_index = 3 if preview else 2
    if len(parts) <= action_index:
        raise ValueError("После rule preview укажи действие.")
    action = parts[action_index].casefold()
    if action == "undo":
        remaining = parts[action_index + 1:]
        kind = value = ""
    else:
        if action not in {"add", "remove", "disable"} or len(parts) <= action_index + 2:
            raise ValueError("Действие rule должно быть add, remove, disable или undo.")
        kind = parts[action_index + 1].casefold()
        if kind not in BLACKLIST_RULE_KINDS:
            raise ValueError("Тип blacklist: vacancy, company, company_role, role или phrase.")
        remaining = parts[action_index + 2:]

    profile_scope = "all"
    expires_at = None
    value_parts: list[str] = []
    index = 0
    while index < len(remaining):
        token = remaining[index]
        if token in {"--profile", "--until"}:
            if index + 1 >= len(remaining):
                raise ValueError(f"После {token} нужно указать значение.")
            option_value = remaining[index + 1]
            if token == "--profile":
                profile_scope = option_value
            else:
                try:
                    expires = datetime.fromisoformat(option_value.replace("Z", "+00:00"))
                    if expires.tzinfo is None:
                        expires = expires.replace(tzinfo=UTC)
                    if len(option_value) == 10:
                        expires += timedelta(days=1)
                except ValueError as exc:
                    raise ValueError("Срок должен быть датой YYYY-MM-DD или ISO timestamp.") from exc
                expires_at = expires.astimezone(UTC).isoformat().replace("+00:00", "Z")
            index += 2
            continue
        value_parts.append(token)
        index += 1
    value = " ".join(value_parts).strip()
    if action != "undo" and not value:
        raise ValueError("Укажи значение правила blacklist.")
    if kind == "company_role":
        company, separator, role = value.partition("|")
        if not separator or not company.strip() or not role.strip():
            raise ValueError("company_role задаётся как Компания|Должность.")
    return {
        "preview": preview,
        "action": action,
        "kind": kind,
        "value": value,
        "profile_scope": profile_scope,
        "expires_at": expires_at,
    }


def update_blacklist_rule(
    settings: dict,
    action: str,
    kind: str = "",
    value: str = "",
    *,
    expires_at: str | None = None,
) -> dict:
    """Apply one reversible structured-rule change to profile JSON settings."""
    result = dict(settings)
    rules = [dict(item) for item in (result.get("blacklist_rules") or []) if isinstance(item, dict)]
    if action == "undo":
        previous = result.pop("_blacklist_rules_undo", None)
        if isinstance(previous, list):
            result["blacklist_rules"] = [dict(item) for item in previous if isinstance(item, dict)]
        return result
    if action not in {"add", "remove", "disable"} or kind not in BLACKLIST_RULE_KINDS or not value.strip():
        raise ValueError("Некорректное изменение structured blacklist.")

    result["_blacklist_rules_undo"] = [dict(item) for item in rules]
    key = (kind, " ".join(value.casefold().split()))
    matching_indexes = [
        index for index, rule in enumerate(rules)
        if (rule.get("kind"), " ".join(str(rule.get("value") or "").casefold().split())) == key
    ]
    if action == "add":
        rule = {"kind": kind, "value": value.strip(), "enabled": True}
        if expires_at:
            rule["expires_at"] = expires_at
        if matching_indexes:
            rules[matching_indexes[0]] = rule
        else:
            rules.append(rule)
    elif action == "remove":
        rules = [rule for index, rule in enumerate(rules) if index not in matching_indexes]
    else:
        for index in matching_indexes:
            rules[index]["enabled"] = False
    result["blacklist_rules"] = rules
    return result


def preview_blacklist_rule(settings: dict, action: str, kind: str = "", value: str = "", *, expires_at: str | None = None) -> dict:
    """Preview a structured rule update while preserving the supplied settings."""
    before = [dict(item) for item in (settings.get("blacklist_rules") or []) if isinstance(item, dict)]
    after_settings = update_blacklist_rule(settings, action, kind, value, expires_at=expires_at)
    after = [dict(item) for item in (after_settings.get("blacklist_rules") or []) if isinstance(item, dict)]
    return {"before": before, "after": after, "settings": after_settings}
