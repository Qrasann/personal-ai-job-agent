from __future__ import annotations

import re

from bs4 import BeautifulSoup


_BAD_MOJIBAKE_MARKERS = ("Ã", "Â", "â", "ð", "\x80", "\x99")
_CURRENCY_TOKEN = r"(?:₽|руб(?:\.|лей|ля|ли)?|RUR|RUB|\$|USD|€|EUR|₾|GEL)"
_NUMBER = r"\d[\d\s\u202f\u00a0]*"
_SALARY_FRAGMENT_RE = re.compile(
    rf"(?:(?:от|до|from|up\s+to)\s+)?{_NUMBER}"
    rf"(?:\s*[–—-]\s*{_NUMBER})?\s*{_CURRENCY_TOKEN}",
    re.IGNORECASE,
)


def repair_mojibake(value: str) -> str:
    text = value or ""
    if not text or not any(marker in text for marker in _BAD_MOJIBAKE_MARKERS):
        return text
    try:
        repaired = text.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text
    before = sum(text.count(marker) for marker in _BAD_MOJIBAKE_MARKERS)
    after = sum(repaired.count(marker) for marker in _BAD_MOJIBAKE_MARKERS)
    return repaired if after < before else text


def clean_html_text(value: str) -> str:
    text = repair_mojibake(value or "")
    if "<" in text and ">" in text:
        text = BeautifulSoup(text, "html.parser").get_text("\n", strip=True)
    lines = [" ".join(line.split()) for line in text.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def salary_fragment(value: str) -> str:
    text = repair_mojibake(value or "").replace("\u202f", " ").replace("\xa0", " ")
    match = _SALARY_FRAGMENT_RE.search(text)
    return " ".join(match.group(0).split()) if match else ""


def parse_salary_text(value: str) -> tuple[int | None, int | None, str | None]:
    fragment = salary_fragment(value) or (value or "")
    if not fragment:
        return None, None, None
    compact = fragment.replace("\u202f", " ").replace("\xa0", " ")
    nums = [int(x.replace(" ", "")) for x in re.findall(r"\d[\d ]{2,}", compact)]
    currency = None
    folded = compact.casefold()
    upper = compact.upper()
    if "₽" in compact or "руб" in folded or "RUR" in upper or "RUB" in upper:
        currency = "RUR"
    elif "$" in compact or "USD" in upper:
        currency = "USD"
    elif "€" in compact or "EUR" in upper:
        currency = "EUR"
    elif "₾" in compact or "GEL" in upper:
        currency = "GEL"
    if not nums:
        return None, None, currency
    if len(nums) >= 2:
        return nums[0], nums[1], currency
    if folded.strip().startswith(("до ", "up to ")):
        return None, nums[0], currency
    return nums[0], None, currency


def format_salary(
    salary_from: int | None,
    salary_to: int | None,
    currency: str | None,
    *,
    fallback_text: str = "",
) -> str:
    low = salary_from if salary_from and salary_from > 0 else None
    high = salary_to if salary_to and salary_to > 0 else None
    curr = (currency or "").upper()

    # Legacy HH rows may contain bogus numeric values because an older parser
    # picked unrelated card numbers (ratings, company names, counters). A
    # currency-bearing salary fragment in the visible source text is more
    # trustworthy. If no currency exists anywhere, do not present old bare
    # integers as salary.
    parsed_low = parsed_high = None
    parsed_currency = None
    if fallback_text:
        parsed_low, parsed_high, parsed_currency = parse_salary_text(fallback_text)
    if parsed_currency and (parsed_low or parsed_high):
        low, high, curr = parsed_low, parsed_high, parsed_currency
    elif not curr:
        low = high = None

    symbol = {"RUR": "₽", "RUB": "₽", "USD": "$", "EUR": "€", "GEL": "₾"}.get(curr, currency or "")

    def money(value: int) -> str:
        return f"{value:,}".replace(",", " ")

    suffix = f" {symbol}" if symbol else ""
    if low and high:
        return f"{money(low)}–{money(high)}{suffix}"
    if low:
        return f"от {money(low)}{suffix}"
    if high:
        return f"до {money(high)}{suffix}"
    return "не указана"


def extract_experience(value: str) -> str:
    text = clean_html_text(value)
    patterns = (
        r"(?:опыт(?:\s+работы)?\s*[:—-]?\s*)(без опыта|не требуется|\d+\s*[–—-]\s*\d+\s*(?:года|год|лет)|от\s+\d+\s*(?:года|лет)|более\s+\d+\s*лет)",
        r"\b(\d+\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience)\b",
        r"\b(experience\s*[:—-]?\s*\d+\s*[–—-]\s*\d+\s*(?:years?|yrs?))\b",
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            value = " ".join(match.group(1).split())
            return value[0].upper() + value[1:] if value else ""
    return ""
