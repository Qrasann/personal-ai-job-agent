import asyncio
import errno
import socket
import ssl
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest

from app import services
from app.sources.base import SourceContext
from app.sources.network_errors import transport_failure_category


@pytest.mark.parametrize("cause, category", [
    (socket.gaierror(-2, "private hostname"), "dns"),
    (ssl.SSLError("private TLS details"), "tls"),
    (ssl.SSLCertVerificationError("private certificate"), "tls_certificate"),
    (OSError(errno.ECONNRESET, "private address"), "connection_reset"),
    (OSError(errno.ECONNREFUSED, "private address"), "connection_refused"),
    (OSError(errno.EHOSTUNREACH, "private address"), "network_unreachable"),
    (httpx.ProxyError("private proxy credentials"), "proxy"),
    (httpx.ConnectTimeout("private URL"), "connect_timeout"),
    (httpx.ReadTimeout("private URL"), "read_timeout"),
    (httpx.PoolTimeout("private URL"), "pool_timeout"),
])
def test_transport_category_uses_typed_causes(cause, category):
    wrapped = httpx.ConnectError("private URL and credentials")
    intermediate = RuntimeError("private transport internals")
    intermediate.__cause__ = cause
    wrapped.__cause__ = intermediate
    assert transport_failure_category(wrapped) == category


def test_transport_category_never_guesses_from_text_and_handles_cycles():
    first = httpx.ConnectError("DNS TLS IPv6 timeout")
    second = RuntimeError("proxy")
    first.__cause__ = second
    second.__cause__ = first
    assert transport_failure_category(first) == "unclassified"


def test_transport_category_ignores_suppressed_context():
    error = httpx.ConnectError("private")
    error.__context__ = socket.gaierror(-2, "unrelated previous lookup")
    error.__suppress_context__ = True
    assert transport_failure_category(error) == "unclassified"


def test_hh_connection_log_has_safe_category_without_payload(monkeypatch, caplog):
    error = httpx.ConnectError("https://hh.test/?token=private-value")
    error.__cause__ = socket.gaierror(-2, "private-hostname")
    adapter = SimpleNamespace(discover=AsyncMock(side_effect=error))
    monkeypatch.setattr(services, "_HH_DISCOVERY_LOCK", asyncio.Lock())
    monkeypatch.setattr(services, "_HH_CONNECT_RETRY_AFTER", 0.0)
    monkeypatch.setattr(services, "_DISCOVERY_CACHE", {})

    with pytest.raises(httpx.ConnectError):
        asyncio.run(services._discover_hh(adapter, SourceContext(user_id=1)))

    assert "category=dns" in caplog.text
    assert "private-value" not in caplog.text
    assert "private-hostname" not in caplog.text
    assert services._HH_CONNECT_RETRY_AFTER > 0


def test_source_error_does_not_infer_http_status_from_text():
    assert services._error_text(RuntimeError("HTTP 503")) == "SOURCE_PROCESSING_FAILED"


def test_source_error_falls_back_to_exception_type():
    assert services._error_text(TimeoutError()) == "SOURCE_DISCOVERY_TIMEOUT"


def test_source_error_reports_http_status():
    request = services.httpx.Request("GET", "https://example.org")
    response = services.httpx.Response(503, request=request)
    error = services.httpx.HTTPStatusError("", request=request, response=response)
    assert services._error_text(error) == "HTTP_5XX_SERVER_ERROR"


def test_transport_error_does_not_expose_request_url_or_credentials():
    request = services.httpx.Request("GET", "https://feed.example/jobs?token=private-value")
    error = services.httpx.ConnectError("connection to https://feed.example/jobs?token=private-value failed", request=request)
    assert services._error_text(error) == "NETWORK_CONNECT_ERROR"


@pytest.mark.parametrize("error, label", [
    (ssl.SSLError("https://feed.test/?token=private-value"), "TLS_CONNECTION_FAILED"),
    (socket.gaierror(-2, "private DNS address"), "DNS_RESOLUTION_FAILED"),
])
def test_raw_network_error_summaries_do_not_expose_payloads(error, label):
    assert services._error_text(error) == label
