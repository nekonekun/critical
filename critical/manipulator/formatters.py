from abc import ABC, abstractmethod

from .models import GELFMessage
from .loggers import formatters_logger as logger


class AbstractFormatter(ABC):
    @abstractmethod  # pragma: no cover
    def __init__(self, **kwargs):
        raise NotImplementedError

    def format(self, obj: GELFMessage) -> str:  # pragma: no cover
        return str(obj)

    @classmethod
    @abstractmethod
    def from_dict(cls, settings: dict):  # pragma: no cover
        raise NotImplementedError


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

    @classmethod
    def from_dict(cls, settings: dict):
        field = settings.get('field')
        return CopyFieldFormatter(field)


class SimpleMailFormatter(AbstractFormatter):
    def __init__(self, subject_field: str,
                 body_field: str,
                 template: str = None,
                 **kwargs):
        self.subject_field = subject_field
        self.body_field = body_field
        self.template = template or 'Subject: {subject}\n\n{body}'

    def format(self, obj: GELFMessage) -> str:
        subject = str(obj.dict(by_alias=True).get(self.subject_field))
        body = str(obj.dict(by_alias=True).get(self.body_field))
        body += '\n\n'
        body += obj.timestamp_.isoformat()
        text = self.template.format(subject=subject, body=body)
        return text

    @classmethod
    def from_dict(cls, settings: dict):
        subject_field = settings.get('subject_field')
        body_field = settings.get('body_field')
        template = settings.get('template')
        return SimpleMailFormatter(subject_field=subject_field,
                                   body_field=body_field,
                                   template=template)


class DummyFormatter(AbstractFormatter):  # pragma: no cover
    def __init__(self, **kwargs):
        pass

    @classmethod
    def from_dict(cls, settings: dict):
        return DummyFormatter()
