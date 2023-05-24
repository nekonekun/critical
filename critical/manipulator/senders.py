from abc import ABC, abstractmethod
from typing import List, Union, Any
from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter, AiogramError
import asyncio
from aiosmtplib import SMTP
from aiosmtplib import SMTPResponseException

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


class MailSender(AbstractAsyncSender):
    def __init__(self, smtp: SMTP,
                 sender: str,
                 receivers: list[str],
                 subject: str = None,
                 settings: dict = None,
                 **kwargs):
        self.smtp = smtp
        self.sender = sender
        self.subject = subject or 'Critical Bot Message'
        self.settings = settings
        super().__init__(receivers, **kwargs)

    async def start(self):
        await self.smtp.connect()

    async def stop(self):
        if self.smtp.is_connected:
            self.smtp.close()

    async def send_one(self, message: str, receiver: Any):
        if self.settings:
            current_smtp = self.smtp_from_dict(self.settings)
        else:
            current_smtp = self.smtp
        headers = f'From: {self.sender}\n'
        if 'Subject: ' not in message:
            headers += f'Subject: {self.subject}\n'
        message_to_send = headers + message
        if not current_smtp.is_connected:
            await current_smtp.connect()
        try:
            await self.smtp.sendmail(self.sender, receiver, message_to_send)
        except SMTPResponseException as e:
            logger.error(str(e))
        finally:
            if self.settings:
                current_smtp.close()

    @classmethod
    def smtp_from_dict(cls, settings: dict):
        hostname = settings.get('hostname')
        port = settings.get('port')
        username = settings.get('username')
        password = settings.get('password')
        use_tls = settings.get('use_tls', True)
        return SMTP(hostname=hostname, port=port,
                    username=username, password=password,
                    use_tls=use_tls)

    @classmethod
    def from_dict(cls, settings: dict):
        smtp = cls.smtp_from_dict(settings=settings)
        sender: str = settings.pop('sender')
        subject: str = settings.pop('subject', 'Critical Bot Message')
        receivers: list = settings.pop('receivers')
        return cls(smtp, sender, receivers, subject, settings)


class TerminalSender(AbstractAsyncSender):  # pragma: no cover
    prefix: str = 'vty_'

    async def send_one(self, message: str, receiver: Any):
        logger.critical(message)

    @classmethod
    def from_dict(cls, settings: dict):
        receivers = settings.get('receivers', [0])
        return TerminalSender(receivers=receivers)


class DummySender(AbstractAsyncSender):  # pragma: no cover
    prefix: str = 'dummy_'

    def __init__(self, receivers, **kwargs):
        super().__init__(receivers, **kwargs)

    async def send_one(self, message: str, receiver: Any):
        pass

    @classmethod
    def from_dict(cls, settings: dict):
        return DummySender([])
