import asyncio
import logging

import aiokafka
import pytest

from critical.manipulator.consumers import AbstractAsyncConsumer
from critical.manipulator.consumers import KafkaAsyncConsumer
from critical.manipulator.models import GELFMessage


@pytest.mark.asyncio
async def test_abstract():
    with pytest.raises(TypeError):
        consumer = AbstractAsyncConsumer()
    AbstractAsyncConsumer.__abstractmethods__ = set()
    consumer = AbstractAsyncConsumer()
    count = await consumer.consumer_target_count()
    assert isinstance(count, int)
    assert count > 0
    assert isinstance(await consumer.fork(), AbstractAsyncConsumer)

    await consumer.start()
    await consumer.stop()

    with pytest.raises(NotImplementedError):
        msg = await consumer.consume()


@pytest.mark.asyncio
async def test_kafka(kafka_creds, kafka_producer, kafka_consumer, composer):
    k_producer = await kafka_producer
    await k_producer.start()
    k_consumer = await kafka_consumer

    topic = kafka_creds.get('topic')
    consumer = KafkaAsyncConsumer(k_consumer, topic)
    await consumer.start()
    count = await consumer.consumer_target_count()
    assert isinstance(count, int)

    fork = await consumer.fork()
    assert fork is not None
    assert isinstance(fork, KafkaAsyncConsumer)
    assert isinstance(fork.consumer, aiokafka.AIOKafkaConsumer)
    await fork.stop()

    # empty the queue
    while True:
        try:
            await asyncio.wait_for(k_consumer.getone(), 1)
        except asyncio.TimeoutError:
            break

    await k_producer.send_and_wait(topic,
                                   composer.message().encode('utf-8'))
    msg = await consumer.consume()
    assert isinstance(msg, GELFMessage)

    await consumer.stop()

    del consumer

    valid_creds = kafka_creds.copy()
    consumer = KafkaAsyncConsumer.from_dict(valid_creds)
    assert isinstance(consumer, KafkaAsyncConsumer)

    with pytest.raises(ValueError):
        invalid_creds = kafka_creds.copy()
        invalid_creds.pop('topic')
        consumer = KafkaAsyncConsumer.from_dict(invalid_creds)

    with pytest.raises(ValueError):
        invalid_creds = kafka_creds.copy()
        invalid_creds.pop('group_id')
        consumer = KafkaAsyncConsumer.from_dict(invalid_creds)

    with pytest.raises(ValueError):
        invalid_creds = kafka_creds.copy()
        invalid_creds['extra'] = 'extra value'
        consumer = KafkaAsyncConsumer.from_dict(invalid_creds)

    await k_producer.stop()
