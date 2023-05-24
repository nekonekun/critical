import ipaddress
from abc import ABC, abstractmethod
from typing import List, Optional, Union
from ipaddress import IPv4Address, IPv4Network
from .models import GELFMessage
from .loggers import filters_logger as logger


class AbstractStaticFilter(ABC):
    @abstractmethod  # pragma: no cover
    def __init__(self, **kwargs):
        raise NotImplementedError

    @abstractmethod  # pragma: no cover
    def filter(self, obj: GELFMessage) -> bool:
        raise NotImplementedError


class SourceIPFilter(AbstractStaticFilter):
    def __init__(self, prefixes: Optional[List[Union[IPv4Network, str]]] = None,
                 ips: Optional[List[Union[IPv4Address, str]]] = None,
                 exclude: bool = False):
        logger.debug('SourceIP filter initializing...')
        self.prefixes = prefixes or []
        self.prefixes = list(map(ipaddress.IPv4Network, self.prefixes))
        logger.debug(f'Prefixes: {self.prefixes}')
        self.ips = ips or []
        self.ips = list(map(ipaddress.IPv4Address, self.ips))
        logger.debug(f'IPs: {self.ips}')
        self.exclude = exclude
        logger.debug(f'Exclude: {self.exclude}')
        logger.info('SourceIP filter has been set')

    def filter(self, obj: GELFMessage) -> bool:
        logger.debug('Start IP source filter process')
        present_in_prefixes = False
        if self.prefixes:
            prefixes = map(lambda x: x.exploded, self.prefixes)
            prefixes = ', '.join(prefixes)
            logger.debug(f'Prefixes: {prefixes}')
            for prefix in self.prefixes:
                if obj.gl2_remote_ip_ in prefix:
                    logger.debug(f'Present in prefix {prefix}')
                    present_in_prefixes = True
        present_in_ip_list = False
        if self.ips:
            ips = map(lambda x: x.exploded, self.ips)
            ips = ', '.join(ips)
            logger.debug(f'IPs: {ips}')
            for ip in self.ips:
                if obj.gl2_remote_ip_ == ip:
                    logger.debug(f'Equal to IP {ip}')
                    present_in_prefixes = True
        logger.debug(f'Exclude: {self.exclude}')
        result = (present_in_prefixes or present_in_ip_list) != self.exclude
        if result:
            logger.debug('Filter passed')
        else:
            logger.debug('Message filtered')
        return result


class MessageBodyFilter(AbstractStaticFilter):
    def __init__(self, pattern: str, exclude: bool = False):
        logger.debug('MessageBody filter initializing...')
        self.pattern = pattern
        logger.debug(f'Pattern: {self.pattern}')
        self.exclude = exclude
        logger.debug(f'Exclude: {self.exclude}')
        logger.info('MessageBody filter has been set')

    def filter(self, obj: GELFMessage) -> bool:
        logger.debug('Start message body filter process')
        logger.debug(f'Pattern: {self.pattern}')
        present_in_message = self.pattern in obj.full_message_
        if present_in_message:
            logger.debug(f'Pattern {self.pattern} found')
        logger.debug(f'Exclude: {self.exclude}')
        result = present_in_message != self.exclude
        if result:
            logger.debug('Filter passed')
        else:
            logger.debug('Message filtered')
        return result


class MessageBodyAnyFilter(AbstractStaticFilter):
    def __init__(self, patterns: List[str], exclude: bool = False):
        self.patterns = patterns
        self.exclude = exclude

    def filter(self, obj: GELFMessage) -> bool:
        logger.debug('Start message body filter process')
        present_in_message = False
        for pattern in self.patterns:
            logger.debug(f'Pattern: {pattern}')
            present_in_message = pattern in obj.full_message_
            if present_in_message:
                logger.debug(f'Pattern {pattern} found')
                present_in_message = True
                break
        logger.debug(f'Exclude: {self.exclude}')
        result = present_in_message != self.exclude
        if result:
            logger.debug('Filter passed')
        else:
            logger.debug('Message filtered')
        return result
