from abc import ABC, abstractmethod

from .models import GELFMessage
from .loggers import formatters_logger as logger


class AbstractFormatter(ABC):
    @abstractmethod  # pragma: no cover
    def __init__(self, **kwargs):
        raise NotImplementedError

    def format(self, obj: GELFMessage) -> str:  # pragma: no cover
        return str(obj)


class CopyFieldFormatter(AbstractFormatter):
    def __init__(self, field: str):
        logger.debug('CopyField formatter initializing...')
        if field.endswith('_'):
            field = '_' + field[:-1]
        self.field = field
        logger.debug(f'Field: {self.field}')
        logger.info('CopyField formatter has been set')

    def format(self, obj: GELFMessage) -> str:
        logger.debug('Start copy field message formatting')
        logger.debug(f'Field: {self.field}')
        result = str(obj.dict(by_alias=True).get(self.field))
        logger.debug(f'Outgoing message: {result}')
        return result
