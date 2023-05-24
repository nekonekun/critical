import redis
from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import TelegramObject
from typing import Callable, Awaitable, Any


class RedisMiddleware(BaseMiddleware):
    def __init__(self, redis_client: redis.Redis):
        super().__init__()
        self.redis_client = redis_client

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:
        is_using_redis = get_flag(data, 'is_using_redis')

        if not is_using_redis:
            return await handler(event, data)

        data['redis_instance'] = self.redis_client
        return await handler(event, data)
