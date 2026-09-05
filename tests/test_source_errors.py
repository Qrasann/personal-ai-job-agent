from app import services


def test_source_error_uses_message_when_present():
    assert services._error_text(RuntimeError("HTTP 503")) == "HTTP 503"


def test_source_error_falls_back_to_exception_type():
    assert services._error_text(TimeoutError()) == "TimeoutError"
