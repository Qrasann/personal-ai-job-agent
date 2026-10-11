from __future__ import annotations

import re


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
    if action == "add" and term.strip():
        if not any(item.casefold() == term.strip().casefold() for item in terms):
            terms.append(term.strip())
    elif action == "remove":
        terms = [item for item in terms if item.casefold() != term.strip().casefold()]
    elif action == "clear":
        terms = []
    result["exclude_terms"] = terms
    return result
