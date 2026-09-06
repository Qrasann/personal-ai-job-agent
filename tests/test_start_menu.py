import inspect
from app.telegram.handlers import start

def test_start_message_has_no_unsupported_html_placeholders():
    source = inspect.getsource(start)
    assert "<id>" not in source
