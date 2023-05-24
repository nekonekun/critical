import pytest

from critical.manipulator.consumers import AbstractAsyncConsumer
from critical.manipulator.consumers import KafkaAsyncConsumer


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
async def test_kafka(kafka_creds):
    consumer = KafkaAsyncConsumer(**kafka_creds)

    assert consumer.consumer is None
    count = await consumer.consumer_target_count()
    assert isinstance(count, int)
    assert count > 0

    with pytest.raises(AttributeError):
        msg = await consumer.consume()

    await consumer.start()
    assert consumer.consumer is not None
    msg = await consumer.consume()
    await consumer.stop()
    assert consumer.consumer is None

    fork = await consumer.fork()
    assert isinstance(fork, KafkaAsyncConsumer)
    assert fork.consumer is not None
    await fork.stop()
    assert fork.consumer is None
