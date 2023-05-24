import asyncio
from collections import defaultdict
import pathlib
import typer
from typing_extensions import Annotated
import yaml

from .consumers import KafkaAsyncConsumer, AbstractAsyncConsumer
from .handler import Handler
from .loggers import customize_logger, main_logger


LOGGING_LEVELS = defaultdict(lambda: 'DEBUG',
                             {0: 'ERROR',
                              1: 'WARNING',
                              2: 'INFO',
                              3: 'DEBUG'})


def typer_main():
    typer.run(main)


def main(config: Annotated[pathlib.Path, typer.Argument()],
         kafka_server: Annotated[str,
                                 typer.Option('--kafka-server')],
         kafka_topic: Annotated[str,
                                typer.Option('--kafka-topic')],
         verbose: Annotated[int,
                            typer.Option('--verbose', '-v', count=True)] = 0):
    customize_logger(LOGGING_LEVELS[verbose])
    main_logger.error('Starting app...')
    with open(config) as f:
        cfg_dict = yaml.safe_load(f)

    if 'name' not in cfg_dict:
        handler_name = pathlib.Path(config).stem
        cfg_dict['name'] = handler_name
    try:
        handler = Handler.from_dict(cfg_dict)
    except AttributeError as e:
        main_logger.critical(str(e))
        return
    main_logger.error('Handler initialized')

    main_logger.info(f'Topic: {kafka_topic}')

    handler_name = handler.name
    handler_name = ''.join(filter(str.isalnum, handler_name)).lower()
    group_id = kafka_topic + '.' + handler_name
    main_logger.info(f'Group ID: {group_id}')

    consumer = KafkaAsyncConsumer(topic=kafka_topic,
                                  bootstrap_servers=kafka_server,
                                  group_id=group_id)
    main_logger.error('Consumer initialized')

    try:
        asyncio.run(_main(consumer, handler))
    except KeyboardInterrupt:
        main_logger.error('Keyboard Interrupt, stop')


async def _main(consumer: AbstractAsyncConsumer,
                handler: Handler):
    workers = []
    for i in range(await consumer.consumer_target_count()):
        worker_task = asyncio.create_task(worker(consumer, i, handler))
        workers.append(worker_task)
    try:
        await handler.start()
        await asyncio.gather(*workers)
    except asyncio.exceptions.CancelledError:
        main_logger.error('Handler cancelled, stop')
    finally:
        await handler.stop()
        main_logger.error('Handler stopped')


async def worker(parent_consumer: AbstractAsyncConsumer,
                 number: int,
                 handler: Handler):
    main_logger.error(f'Start consumer #{number}')
    if number == 0:
        consumer = parent_consumer
        await consumer.start()
    else:
        consumer = await parent_consumer.fork()
    try:
        while True:
            msg = await consumer.consume()
            main_logger.info(f'Consumer #{number} get new message')
            main_logger.debug(msg.full_message)
            await handler.handle(msg)
    except asyncio.CancelledError:
        main_logger.error(f'Consumer #{number} cancelled, stop')
    finally:
        await consumer.stop()
        main_logger.error(f'Consumer #{number} stopped')
