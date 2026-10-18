from types import SimpleNamespace

import pytest

from app.telegram.handlers import router as job_router
from app.telegram.settings_handlers import router as settings_router


@pytest.mark.parametrize("router", [job_router, settings_router])
def test_candidate_commands_and_callbacks_only_route_from_private_chat(router):
    message_filter = router.message._handler.filters[0].magic
    callback_filter = router.callback_query._handler.filters[0].magic
    for chat_type, expected in (("private", True), ("group", False), ("supergroup", False)):
        message = SimpleNamespace(chat=SimpleNamespace(type=chat_type))
        callback = SimpleNamespace(message=message)
        assert message_filter.resolve(message) is expected
        assert callback_filter.resolve(callback) is expected


def test_channel_post_observer_is_not_filtered_by_private_chat_rule():
    assert not job_router.channel_post._handler.filters
