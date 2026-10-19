from __future__ import annotations

import html
import json
import re

import httpx

from app.providers.hh import HHAPIForbidden, HHCaptchaRequired
from app.sources.network_errors import transport_failure_category


class SourceInvalidResponse(ValueError):
    """A response violates a verified adapter contract."""


class SourceSummaryError(ValueError):
    """Application statistics violate their required shape."""


MESSAGES = {
    "NETWORK_CONNECT_TIMEOUT": "Не удалось установить соединение за отведённое время.",
    "NETWORK_READ_TIMEOUT": "Ответ не поступил вовремя при чтении соединения.",
    "NETWORK_POOL_TIMEOUT": "Не удалось дождаться свободного соединения HTTP-клиента.",
    "NETWORK_CONNECT_ERROR": "Не удалось установить соединение с источником.",
    "DNS_RESOLUTION_FAILED": "Не удалось определить сетевой адрес сервиса.",
    "TLS_VALIDATION_FAILED": "Не удалось проверить сертификат защищённого соединения.",
    "TLS_CONNECTION_FAILED": "Ошибка защищённого соединения.",
    "NETWORK_PROXY_ERROR": "Ошибка соединения через прокси.",
    "NETWORK_CONNECTION_RESET": "Соединение было сброшено.",
    "NETWORK_CONNECTION_REFUSED": "Подключение было отклонено.",
    "NETWORK_UNREACHABLE": "Сетевой маршрут до сервиса недоступен.",
    "NETWORK_TRANSPORT_FAILED": "Ошибка передачи данных по сети.",
    "HTTP_403_FORBIDDEN": "Источник отказал в доступе к запросу.",
    "HTTP_429_RATE_LIMITED": "Источник ограничил частоту обращений.",
    "HTTP_5XX_SERVER_ERROR": "Сервер источника вернул ошибку.",
    "HTTP_REQUEST_FAILED": "Источник вернул неуспешный HTTP-ответ.",
    "SOURCE_INVALID_RESPONSE": "Ответ источника имеет неожиданный формат.",
    "SOURCE_SUMMARY_MISSING_FIELD": "Внутренняя ошибка статистики поиска.",
    "SOURCE_PROCESSING_FAILED": "Внутренняя ошибка обработки данных источника.",
    "SOURCE_DISCOVERY_TIMEOUT": "Сбор вакансий превысил допустимое время.",
    "SOURCE_ACCESS_CHALLENGE": "Источник требует ручной проверки доступа.",
    "SOURCE_PARTIAL_RESULTS": "Часть запросов источника завершилась с ошибкой.",
    "SOURCE_CONNECTION_COOLDOWN": "Источник временно пропущен после ошибки соединения.",
    "SOURCE_NOTICE_DELIVERY_FAILED": "Не удалось доставить техническое уведомление; причина источника сохранена.",
}
STAGES = {
    "discovery": "сбор вакансий", "response": "разбор ответа",
    "processing": "обработка вакансий", "summary": "статистика приложения",
    "connection": "установка соединения", "read": "чтение ответа",
    "pool": "ожидание соединения", "dns": "DNS", "tls": "TLS",
    "proxy": "прокси", "http": "HTTP-ответ", "search_request": "поисковый запрос",
    "detail_request": "получение описания", "scan": "выполнение поиска",
    "notification": "доставка технического уведомления",
}
ACTION_TEXT = {
    "continue": "Источник пропущен для этих профилей; поиск по другим источникам продолжен.",
    "continue_partial": "Сохранённые результаты не отменены; обработка остальных продолжена.",
    "cooldown": "Повторная проверка HH — после паузы до 15 минут; другие источники продолжают работу.",
    "fallback": "Использован разрешённый публичный fallback HH.",
    "stop_source": "Дальнейшие запросы к этому источнику прекращены; другие источники продолжают работу.",
    "summary": "Вакансии продолжают обрабатываться; статистика помечена неполной.",
    "inspect_dashboard": "Подробности сохранены в диагностике; дополнительное сообщение не отправляется.",
}
_NETWORK_CODES = {
    "dns": ("DNS_RESOLUTION_FAILED", "dns"),
    "tls_certificate": ("TLS_VALIDATION_FAILED", "tls"),
    "tls": ("TLS_CONNECTION_FAILED", "tls"),
    "proxy": ("NETWORK_PROXY_ERROR", "proxy"),
    "connect_timeout": ("NETWORK_CONNECT_TIMEOUT", "connection"),
    "read_timeout": ("NETWORK_READ_TIMEOUT", "read"),
    "pool_timeout": ("NETWORK_POOL_TIMEOUT", "pool"),
    "connection_reset": ("NETWORK_CONNECTION_RESET", "connection"),
    "connection_refused": ("NETWORK_CONNECTION_REFUSED", "connection"),
    "network_unreachable": ("NETWORK_UNREACHABLE", "connection"),
}


def diagnostic(code: str, *, stage: str = "discovery", action: str = "continue", **fields) -> dict:
    code = code if code in MESSAGES else "SOURCE_PROCESSING_FAILED"
    return {"code": code, "message": MESSAGES[code],
            "stage": stage if stage in STAGES else "discovery",
            "action": action if action in ACTION_TEXT else "continue", "count": 1, **fields}


def classify_source_error(exc: Exception, *, stage: str = "discovery", action: str = "continue") -> dict:
    if isinstance(exc, SourceSummaryError) or (stage == "summary" and isinstance(exc, KeyError)):
        return diagnostic("SOURCE_SUMMARY_MISSING_FIELD", stage="summary", action="summary")
    if isinstance(exc, HHAPIForbidden):
        return diagnostic("HTTP_403_FORBIDDEN", stage="http", action=action, http_status=403)
    if isinstance(exc, HHCaptchaRequired):
        return diagnostic("SOURCE_ACCESS_CHALLENGE", stage="http", action=action)
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        code = {403: "HTTP_403_FORBIDDEN", 429: "HTTP_429_RATE_LIMITED"}.get(status)
        code = code or ("HTTP_5XX_SERVER_ERROR" if 500 <= status < 600 else "HTTP_REQUEST_FAILED")
        return diagnostic(code, stage="http", action=action, http_status=status)
    category = transport_failure_category(exc)
    if category in _NETWORK_CODES:
        code, observed_stage = _NETWORK_CODES[category]
        return diagnostic(code, stage=observed_stage, action=action)
    if isinstance(exc, httpx.ConnectError):
        return diagnostic("NETWORK_CONNECT_ERROR", stage="connection", action=action)
    if isinstance(exc, httpx.TransportError):
        return diagnostic("NETWORK_TRANSPORT_FAILED", stage=stage, action=action)
    if isinstance(exc, (SourceInvalidResponse, json.JSONDecodeError)):
        return diagnostic("SOURCE_INVALID_RESPONSE", stage="response", action=action)
    if isinstance(exc, TimeoutError) and stage == "discovery":
        return diagnostic("SOURCE_DISCOVERY_TIMEOUT", stage=stage, action=action)
    return diagnostic("SOURCE_PROCESSING_FAILED", stage=stage, action=action)


def legacy_diagnostic(value) -> dict:
    """Read old dashboard errors without redisplaying their raw text."""
    value = html.unescape(str(value or ""))
    if value in MESSAGES:
        return diagnostic(value)
    known = {"ConnectTimeout": "NETWORK_CONNECT_TIMEOUT", "ReadTimeout": "NETWORK_READ_TIMEOUT",
             "PoolTimeout": "NETWORK_POOL_TIMEOUT", "ConnectError": "NETWORK_CONNECT_ERROR",
             "SSLError": "TLS_CONNECTION_FAILED", "gaierror": "DNS_RESOLUTION_FAILED",
             "'found'": "SOURCE_SUMMARY_MISSING_FIELD", '"found"': "SOURCE_SUMMARY_MISSING_FIELD"}
    if value in known:
        stage = {"ConnectTimeout": "connection", "ReadTimeout": "read", "PoolTimeout": "pool",
                 "ConnectError": "connection", "SSLError": "tls", "gaierror": "dns"}.get(value, "summary")
        return diagnostic(known[value], stage=stage)
    match = re.fullmatch(r"HTTP ([1-5][0-9]{2})", value)
    if match:
        status = int(match[1])
        code = {403: "HTTP_403_FORBIDDEN", 429: "HTTP_429_RATE_LIMITED"}.get(status)
        return diagnostic(code or ("HTTP_5XX_SERVER_ERROR" if status >= 500 else "HTTP_REQUEST_FAILED"), stage="http")
    return diagnostic("SOURCE_PROCESSING_FAILED")


def render_source_notice(profiles: list[str], source: str, item: dict, *, preserved: bool = False) -> str:
    code = item.get("code") if item.get("code") in MESSAGES else "SOURCE_PROCESSING_FAILED"
    stage = STAGES.get(item.get("stage"), STAGES["discovery"])
    if item.get("operation") in STAGES:
        stage = STAGES[item["operation"]] + " / " + stage
    scope = " / ".join(html.unescape(str(name))[:128] for name in dict.fromkeys(profiles))
    impact = "Получены частичные результаты." if preserved else "Результаты этой попытки недоступны."
    if item.get("action") == "fallback":
        impact = "Сбор через API заменён публичным поиском."
    cause = " Причина устанавливается." if code in {"NETWORK_CONNECT_ERROR", "NETWORK_CONNECT_TIMEOUT", "SOURCE_PROCESSING_FAILED"} else ""
    return (f"⚠️ {scope} · источник {html.unescape(source)}\n"
            f"{MESSAGES[code]} Этап: {stage}.{cause}\n"
            f"{impact} {ACTION_TEXT.get(item.get('action'), ACTION_TEXT['continue'])}\nКод: {code}")
