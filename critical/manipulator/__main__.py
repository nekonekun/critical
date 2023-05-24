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
         kafka_server: Annotated[
             str, typer.Option('--kafka-server',
                               envvar='CRITICAL_KAFKA_SERVER',
                               show_envvar=True)],
         etc_path: Annotated[
             str, typer.Option('--etc-path',
                               envvar='CRITICAL_ETC_PATH',
                               show_envvar=True)] = '',
         verbose: Annotated[
             int, typer.Option('--verbose', '-v',
                               count=True,
                               envvar='CRITICAL_VERBOSITY',
                               show_envvar=True)] = 0):
    customize_logger(LOGGING_LEVELS[verbose])
    main_logger.error('Starting app...')

    full_path = pathlib.Path(etc_path) / config
    with open(full_path) as f:
        handler_dict = yaml.safe_load(f)

    if 'name' not in handler_dict:
        handler_name = pathlib.Path(config).stem
        handler_dict['name'] = handler_name

    consumer_dict = {'bootstrap_servers': kafka_server}

    try:
        asyncio.run(_main(consumer_dict, handler_dict))
    except KeyboardInterrupt:
        main_logger.error('Keyboard Interrupt, stop')


async def _main(consumer_dict: dict,
                handler_dict: dict):
    try:
        handler = Handler.from_dict(handler_dict)
    except AttributeError as e:
        main_logger.critical(str(e))
        return
    main_logger.error('Handler initialized')

    topic = handler.consumer_specification
    handler_name = ''.join(filter(str.isalnum, handler.name)).lower()
    group_id = topic + ':' + handler_name
    consumer_dict['topic'] = topic
    consumer_dict['group_id'] = group_id
    consumer = KafkaAsyncConsumer.from_dict(consumer_dict)
    main_logger.error('Consumer initialized')
    await consumer.start()

    workers = []
    count = await consumer.consumer_target_count()
    for i in range(count):
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
    if number == 1:
        consumer = parent_consumer
    else:
        consumer = await parent_consumer.fork()
    while True:
        try:
            msg = await consumer.consume()
            main_logger.info(f'Consumer #{number} get new message')
            main_logger.debug(msg.short_message)
            await handler.handle(msg)
        except asyncio.CancelledError:
            main_logger.error(f'Stopping consumer #{number}')
            await consumer.stop()
            main_logger.error(f'Consumer #{number} stopped')
            break
        except Exception as e:
            error_text = e.__class__.__name__ + ': ' + str(e)
            main_logger.error(error_text)

