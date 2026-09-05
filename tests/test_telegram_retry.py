import asyncio

import pytest
from aiogram.exceptions import TelegramNetworkError
from aiogram.methods import GetMe

from app.main import wait_for_telegram


class FakeBot:
    def __init__(self, network_failures: int = 0, final_error: Exception | None = None):
        self.network_failures = network_failures
        self.final_error = final_error
        self.calls = 0

    async def me(self):
        self.calls += 1

        if self.calls <= self.network_failures:
            raise TelegramNetworkError(
                method=GetMe(),
                message="temporary timeout",
            )

        if self.final_error is not None:
            raise self.final_error

        return object()


def test_wait_for_telegram_retries_network_errors_with_capped_backoff():
    bot = FakeBot(network_failures=5)
    delays: list[float] = []

    async def fake_sleep(delay: float) -> None:
        delays.append(delay)

    asyncio.run(
        wait_for_telegram(
            bot,
            initial_delay=5,
            max_delay=20,
            sleep=fake_sleep,
        )
    )

    assert bot.calls == 6
    assert delays == [5, 10, 20, 20, 20]


def test_wait_for_telegram_returns_immediately_when_api_is_available():
    bot = FakeBot()
    delays: list[float] = []

    async def fake_sleep(delay: float) -> None:
        delays.append(delay)

    asyncio.run(wait_for_telegram(bot, sleep=fake_sleep))

    assert bot.calls == 1
    assert delays == []


def test_wait_for_telegram_does_not_hide_non_network_errors():
    bot = FakeBot(final_error=RuntimeError("bad configuration"))

    with pytest.raises(RuntimeError, match="bad configuration"):
        asyncio.run(wait_for_telegram(bot))
