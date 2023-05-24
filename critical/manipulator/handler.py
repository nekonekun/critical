from typing import List, Union, Type, TypeVar

from critical.manipulator import formatters, static_filters, \
    dynamic_filters, senders

from .static_filters import AbstractStaticFilter
from .dynamic_filters import AbstractDynamicFilter
from .formatters import AbstractFormatter
from .loggers import handlers_logger as logger
from .models import GELFMessage
from .senders import AbstractAsyncSender


AnyHandler = TypeVar('AnyHandler', bound='Handler')


class Handler:
    def __init__(
            self,
            static_filter_list: Union[List[AbstractStaticFilter],
                                      AbstractStaticFilter],
            dynamic_filter_list: Union[List[AbstractDynamicFilter],
                                       AbstractDynamicFilter],
            formatter: AbstractFormatter,
            sender_list: Union[List[AbstractAsyncSender], AbstractAsyncSender],
            name: str = 'Unnamed Handler'):
        logger.debug('Handler initializing')
        if isinstance(static_filter_list, list):
            self.static_filters = static_filter_list
        else:
            self.static_filters = [static_filter_list]
        logger.error(f'STATIC FILTERS COUNT: {len(self.static_filters)}')
        if isinstance(dynamic_filter_list, list):
            self.dynamic_filters = dynamic_filter_list
        else:
            self.dynamic_filters = [dynamic_filter_list]
        logger.error(f'DYNAMIC FILTERS COUNT: {len(self.dynamic_filters)}')
        self.formatter = formatter

        if isinstance(sender_list, list):
            self.senders = sender_list
        else:
            self.senders = [sender_list]
        self.name = name
        self.middlewares = []
        logger.info(f'{self.name} handler has been set')

    async def start(self) -> None:
        for sender in self.senders:
            await sender.start()
        for dynamic_filter in self.dynamic_filters:
            await dynamic_filter.start()

    async def stop(self) -> None:
        for sender in self.senders:
            await sender.stop()
        for dynamic_filter in self.dynamic_filters:
            await dynamic_filter.stop()

    async def handle(self, obj: GELFMessage) -> None:
        if not all(filter_.filter(obj) for filter_ in self.static_filters):
            return
        message = self.formatter.format(obj)
        for sender in self.senders:
            await sender.send(message, self.dynamic_filters)

    @classmethod
    def from_dict(cls, config: dict) -> AnyHandler:
        logger.info('Creating handler from dict...')
        formatter_settings = config.get('formatter')
        formatter_cls_name = formatter_settings.pop('class')
        try:
            formatter_cls: Type[AbstractFormatter] = getattr(
                formatters, formatter_cls_name)
        except AttributeError:
            logger.critical(f'Formatter class {formatter_cls_name} '
                            f'does not exist')
            raise
        formatter = formatter_cls(**formatter_settings)

        senders_ = []
        all_senders_settings = config.pop('senders')
        for sender_settings in all_senders_settings:
            sender_cls_name = sender_settings.pop('class')
            try:
                sender_cls: Type[AbstractAsyncSender] = getattr(
                    senders, sender_cls_name)
            except AttributeError:
                logger.critical(f'Sender class {sender_cls_name} '
                                f'does not exist')
                raise
            sender = sender_cls(**sender_settings)
            senders_.append(sender)

        static_filters_ = []
        all_static_filters_settings = config.get('static_filters', [])
        for static_filter_settings in all_static_filters_settings:
            filter_cls_name = static_filter_settings.pop('class')
            try:
                filter_cls: Type[AbstractStaticFilter] = getattr(
                    static_filters, filter_cls_name)
            except AttributeError:
                logger.critical(f'Filter class {filter_cls_name} '
                                f'does not exist')
                raise
            filter_ = filter_cls(**static_filter_settings)
            static_filters_.append(filter_)

        dynamic_filters_ = []
        all_dynamic_filters_settings = config.get('dynamic_filters', [])
        for dynamic_filter_settings in all_dynamic_filters_settings:
            filter_cls_name = dynamic_filter_settings.pop('class')
            try:
                filter_cls: Type[AbstractDynamicFilter] = getattr(
                    dynamic_filters, filter_cls_name)
            except AttributeError:
                logger.critical(f'Filter class {filter_cls_name} '
                                f'does not exist')
                raise
            filter_ = filter_cls(**dynamic_filter_settings)
            dynamic_filters_.append(filter_)

        name = config.get('name')
        logger.debug(f'Handler name: {name}')
        return cls(static_filters_, dynamic_filters_, formatter, senders_, name)
