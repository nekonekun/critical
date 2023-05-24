import re
from abc import ABC, abstractmethod
import redis.asyncio as redis
from typing import Optional
from .loggers import filters_logger as logger


class AbstractDynamicFilter(ABC):
    @abstractmethod
    def __init__(self, **kwargs):  # pragma: no cover
        raise NotImplementedError

    @abstractmethod
    async def filter(self, message: str, key: str) -> bool:  # pragma: no cover
        raise NotImplementedError

    async def start(self):  # pragma: no cover
        pass

    async def stop(self):  # pragma: no cover
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, settings: dict):  # pragma: no cover
        raise NotImplementedError


class RedisDynamicFilter(AbstractDynamicFilter, ABC):
    def __init__(self, redis_instance: redis.Redis):
        self.redis = redis_instance

    async def stop(self):
        await self.redis.close()

    @classmethod
    def from_dict(cls, settings: dict):
        host = settings.get('host', 'localhost')
        port = settings.get('port', 6379)
        db = settings.get('db', 0)
        redis_instance = redis.Redis(host=host, port=port, db=db,
                                     decode_responses=True)
        return cls(redis_instance)


class RedisExcludePattern(RedisDynamicFilter):
    async def filter(self, message: str, key: str) -> bool:  # pragma: no cover
        patterns = await self.redis.smembers(key)
        pattern_present = any(pattern in message
                              for pattern in patterns)
        return pattern_present


class RedisExcludeRegexp(RedisDynamicFilter):
    async def filter(self, message: str, key: str) -> bool:
        patterns = await self.redis.smembers(key)
        hit = False
        for pattern in patterns:
            try:
                regexp = re.compile(pattern)
            except re.error:
                hit = pattern in message
            else:
                hit = regexp.search(message) is not None
            if hit:
                break
        return hit


class DummyDynamicFilter(AbstractDynamicFilter):  # pragma: no cover
    def __init__(self, drop: bool = True, **kwargs):
        self.drop = drop

    async def filter(self, message: str, key: str) -> bool:
        return self.drop

    @classmethod
    def from_dict(cls, settings: dict):
        drop = settings.get('drop', True)
        return DummyDynamicFilter(drop)
