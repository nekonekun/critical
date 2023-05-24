from abc import ABC, abstractmethod
import aiokafka
from typing import Optional, TypeVar
import json
from .models import GELFMessage
from .loggers import consumers_logger as logger

AnyAsyncConsumer = TypeVar('AnyAsyncConsumer', bound='AbstractAsyncConsumer')
AnyKafkaConsumer = TypeVar('AnyKafkaConsumer', bound='KafkaConsumer')


class AbstractAsyncConsumer(ABC):
    async def start(self) -> None:
        pass

    async def stop(self) -> None:
        pass

    async def consumer_target_count(self) -> int:
        return 1

    async def fork(self) -> AnyAsyncConsumer:
        return self

    @abstractmethod
    async def consume(self) -> GELFMessage:  # pragma: no cover
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_dict(cls, settings: dict):  # pragma: no cover
        raise NotImplementedError


class KafkaAsyncConsumer(AbstractAsyncConsumer):
    def __init__(self, consumer: aiokafka.AIOKafkaConsumer, topic: str):
        self.consumer = consumer
        self.topic = topic

    async def start(self) -> None:
        """Set up consumer"""
        await self.consumer.start()

    async def stop(self) -> None:
        """Dispose consumer and delete all connections"""
        await self.consumer.stop()

    async def consumer_target_count(self) -> int:
        """Get target count of concurrent consumers"""
        logger.debug('Getting target count of concurrent consumers...')
        partitions = self.consumer.partitions_for_topic(self.topic)
        logger.debug('Got list of partitions')
        result = len(partitions)
        return result

    async def fork(self) -> AnyKafkaConsumer:
        """Create copy of consumer and set it up"""
        new_consumer = aiokafka.AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.consumer._client._bootstrap_servers,
            group_id=self.consumer._group_id,
            enable_auto_commit=True
        )
        child_consumer = KafkaAsyncConsumer(new_consumer, self.topic)
        await child_consumer.start()
        return child_consumer

    async def consume(self) -> GELFMessage:
        """Get another GELF message"""
        msg = await self.consumer.getone()
        value = msg.value.decode('utf-8')
        json_value = json.loads(value)
        message = GELFMessage(**json_value)
        return message

    @classmethod
    def from_dict(cls, settings: dict):
        bootstrap_servers = settings.pop('bootstrap_servers', 'localhost')

        try:
            topic = settings.pop('topic')
        except KeyError:
            raise ValueError('Kafka topic is not provided')
        try:
            group_id = settings.pop('group_id')
        except KeyError:
            raise ValueError('Kafka group ID is not provided')

        if settings:
            raise ValueError('Unexpected key(s): ' + ', '.join(settings.keys()))

        consumer = aiokafka.AIOKafkaConsumer(
                    topic,
                    bootstrap_servers=bootstrap_servers,
                    group_id=group_id,
                    enable_auto_commit=True)
        return cls(consumer, topic)
