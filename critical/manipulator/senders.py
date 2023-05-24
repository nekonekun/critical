from abc import ABC, abstractmethod
from typing import List, Union, Any
from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter, AiogramError
import asyncio

from .loggers import senders_logger as logger
from .dynamic_filters import AbstractDynamicFilter


class AbstractAsyncSender(ABC):
    prefix: str

    def __init__(self, receivers: List[Any], **kwargs):
        """
        Base sender initialization
        :param receivers: destinations (it could be telegram chat IDs,
        e-mails, filenames, etc. based on concrete sender realization)
        :param kwargs: any kwargs needed by concrete sender
        """
        self.receivers = receivers
        receivers_list = ', '.join(map(str, self.receivers))
        logger.debug(f'Receivers: {receivers_list}')

    async def send(self, message: str,
                   dynamic_filters: List[AbstractDynamicFilter] = None):
        """
        :param message:
        :param dynamic_filters:
        :return:
        """
        if not dynamic_filters:
            dynamic_filters = []
        send_tasks = []
        for receiver in self.receivers:
            filtered = False
            for dynamic_filter in dynamic_filters:
                if await dynamic_filter.filter(message,
                                               self.prefix + str(receiver)):
                    filtered = True
                    break
            if not filtered:
                send_tasks.append(self.send_one(message, receiver))
        await asyncio.gather(*send_tasks)

    @abstractmethod
    async def send_one(self, message: str, receiver: Any):  # pragma: no cover
        pass

    async def start(self) -> None:  # pragma: no cover
        pass

    async def stop(self) -> None:  # pragma: no cover
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, settings: dict):  # pragma: no cover
        raise NotImplementedError


class TelegramSender(AbstractAsyncSender):
    prefix: str = 'tg_'

    def __init__(self, bot: Bot, receivers: List[Union[int, str]]):
        """

        :param token:
        :param receivers:
        """
        logger.debug('Telegram sender initializing...')
        # self._token = token
        # bot_id, token_part = self._token.split(':')
        # hidden_token_part = '#' * len(token_part)
        # hidden_token = bot_id + ':' + hidden_token_part
        # logger.debug(f'Token: {hidden_token}')
        self.bot = bot
        super().__init__(receivers)
        logger.info('Telegram sender has been set')

    async def stop(self) -> None:
        """
        Close bot session and dispose bot
        :return: None
        """
        await self.bot.session.close()

    async def send_one(self, message: str, receiver: Union[str, int]) -> None:
        """
        Send message to specified chat
        Wait on timeout error, exit on other errors
        :param message: text to send
        :param receiver: chat_id
        :return: None
        """
        while True:
            try:
                await self.bot.send_message(receiver, message)
                return
            except TelegramRetryAfter as e:
                logger.warning(str(e))
                await asyncio.sleep(e.retry_after)
            except AiogramError as e:
                logger.error(str(e))
                return

    @classmethod
    def from_dict(cls, settings: dict):
        token = settings.get('token')
        receivers = settings.get('receivers')
        bot = Bot(token=token)
        return cls(bot, receivers)


class DummySender(AbstractAsyncSender):  # pragma: no cover
    prefix: str = 'dummy_'

    def __init__(self, receivers, **kwargs):
        super().__init__(receivers, **kwargs)

    async def send_one(self, message: str, receiver: Any):
        pass

    @classmethod
    def from_dict(cls, settings: dict):
        return DummySender([])
