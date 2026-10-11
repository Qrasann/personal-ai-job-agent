from app import services


def test_source_error_uses_message_when_present():
    assert services._error_text(RuntimeError("HTTP 503")) == "HTTP 503"


def test_source_error_falls_back_to_exception_type():
    assert services._error_text(TimeoutError()) == "TimeoutError"


def test_source_error_reports_http_status():
    request = services.httpx.Request("GET", "https://example.org")
    response = services.httpx.Response(503, request=request)
    error = services.httpx.HTTPStatusError("", request=request, response=response)
    assert services._error_text(error) == "HTTP 503"
