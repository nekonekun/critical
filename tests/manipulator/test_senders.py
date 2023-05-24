import pytest

from critical.manipulator.senders import TelegramSender
from critical.manipulator.dynamic_filters import AbstractDynamicFilter


class DummyFilter(AbstractDynamicFilter):
    def __init__(self):
        self.valid = True

    async def filter(self, message: str, key: str) -> bool:
        self.valid = not self.valid
        return self.valid


@pytest.mark.asyncio
async def test_sender(telegram_token, telegram_chat_id):
    sender = TelegramSender(telegram_token, [telegram_chat_id, telegram_chat_id])
    await sender.start()
    assert sender.bot is not None
    await sender.send('test', [DummyFilter()])
    await sender.stop()
    assert sender.bot is None
