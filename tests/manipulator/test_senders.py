import datetime

import pytest
from aiogram.methods import Request, SendMessage
from aiogram.types import Chat, ForceReply, Message

from critical.manipulator.dynamic_filters import AbstractDynamicFilter
from critical.manipulator.senders import TelegramSender


class DummyFilter(AbstractDynamicFilter):
    def __init__(self, valid: bool = True, **kwargs):
        self.valid = valid

    @classmethod
    def from_dict(cls, settings: dict):
        valid = settings.get('valid', True)
        return DummyFilter(valid)

    async def filter(self, message: str, key: str) -> bool:
        return self.valid


@pytest.mark.asyncio
async def test_senders(telegram_bot, telegram_chat_ids, telegram_creds):
    sender = TelegramSender(telegram_bot, telegram_chat_ids)
    # set up dummy filter that filters out all messages
    for chat_id in telegram_chat_ids:
        telegram_bot.add_result_for(
            SendMessage,
            ok=True,
            result=Message(
                message_id=chat_id,
                date=datetime.datetime.now(),
                text='test',
                chat=Chat(id=chat_id, type='private'),
            ),
        )
    await sender.send('test', [DummyFilter.from_dict({})])

    # set up dummy filter that accept all messages
    for chat_id in telegram_chat_ids:
        telegram_bot.add_result_for(
            SendMessage,
            ok=True,
            result=Message(
                message_id=chat_id,
                date=datetime.datetime.now(),
                text='test',
                chat=Chat(id=chat_id, type='private'),
            ),
        )
    await sender.send('test', [DummyFilter(False)])

    # Test flood (error 420) exception
    sender.receivers = [42]
    telegram_bot.add_result_for(
        SendMessage,
        ok=True,
        result=Message(
            message_id=42,
            date=datetime.datetime.now(),
            text='test',
            chat=Chat(id=42, type='private'),
        ),
    )
    telegram_bot.add_result_for(
        SendMessage,
        ok=False,
        error_code=420,
        retry_after=2,
    )
    await sender.send('test')

    # Test other (non-420) errors
    telegram_bot.add_result_for(
        SendMessage,
        ok=True,
        result=Message(
            message_id=42,
            date=datetime.datetime.now(),
            text='test',
            chat=Chat(id=42, type='private'),
        ),
    )
    telegram_bot.add_result_for(
        SendMessage,
        ok=False,
        error_code=400,
    )
    await sender.send('test')
    await sender.stop()

    sender = TelegramSender.from_dict(telegram_creds)
    await sender.stop()
