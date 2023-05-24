import asyncio
import redis.asyncio as redis
import typer
from typing_extensions import Annotated
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from .router import router
from .middlewares import RedisMiddleware
import logging
from rich.logging import RichHandler, Console
from collections import defaultdict
import aiogram.loggers
FORMAT = '<%(name)s> %(message)s'
logging.basicConfig(format=FORMAT,
                    datefmt="[%X]",
                    handlers=[RichHandler(console=Console(width=120),
                                          omit_repeated_times=False)])
LOGGING_LEVELS = defaultdict(lambda: 'DEBUG',
                             {0: 'ERROR',
                              1: 'WARNING',
                              2: 'INFO',
                              3: 'DEBUG'})
logger = logging.getLogger('aiogram')


def typer_main():
    typer.run(main)


def main(bot_token: Annotated[str, typer.Option('--bot-token')],
         redis_host: Annotated[str, typer.Option('--redis-host')] = 'localhost',
         redis_port: Annotated[int, typer.Option('--redis-port')] = 6379,
         redis_db: Annotated[int, typer.Option('--redis-db')] = 0,
         verbose: Annotated[int,
                            typer.Option('--verbose', '-v', count=True)] = 0
         ):
    logger.setLevel(LOGGING_LEVELS[verbose])
    try:
        asyncio.run(_main(bot_token, redis_host, redis_port, redis_db))
    except KeyboardInterrupt:
        logger.info('Cancelled via keyboard')


async def _main(bot_token, redis_host, redis_port, redis_db):
    bot = Bot(token=bot_token, parse_mode='html')
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(router)

    redis_ = redis.Redis(host=redis_host, port=redis_port, db=redis_db,
                         decode_responses=True)
    dp.message.middleware(RedisMiddleware(redis_))

    try:
        await dp.start_polling(bot)
    except asyncio.exceptions.CancelledError:
        logger.info('Cancelled')
    finally:
        await bot.session.close()
        await redis_.close()
