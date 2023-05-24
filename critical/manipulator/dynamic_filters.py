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


class RedisDynamicFilter(AbstractDynamicFilter, ABC):
    def __init__(self, host: str, port: int = 6379, db: int = 0):
        """
        Initialize Redis instance
        :param host: redis host
        :param port: redis port (default: 6379)
        :param db: redis database number (default: 0)
        """
        self.host = host
        self.port = port
        self.db = db
        self.redis: Optional[redis.Redis] = None

    async def start(self):
        self.redis = redis.Redis(host=self.host,
                                 port=self.port,
                                 db=self.db,
                                 decode_responses=True)

    async def stop(self):
        await self.redis.close()
        self.redis = None


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
