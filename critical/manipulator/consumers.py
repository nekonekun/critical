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
    async def consume(self) -> GELFMessage:
        raise NotImplementedError


class KafkaAsyncConsumer(AbstractAsyncConsumer):
    def __init__(self, bootstrap_servers: str, topic: str, group_id: str):
        """
        :param bootstrap_servers: bootstrap servers separated by comma
        :param topic: kafka topic
        :param group_id: consumer group ID
        """
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.group_id = group_id
        self.consumer: Optional[aiokafka.AIOKafkaConsumer] = None

    async def start(self) -> None:
        """Set up consumer"""
        self.consumer = aiokafka.AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            enable_auto_commit=True)
        await self.consumer.start()

    async def stop(self) -> None:
        """Dispose consumer and delete all connections"""
        await self.consumer.stop()
        self.consumer = None

    async def consumer_target_count(self) -> int:
        """Get target count of concurrent consumers"""
        logger.debug('Getting target count of concurrent consumers...')
        disabled = self.consumer is None
        if disabled:
            logger.debug('Consumers is not running, start')
            await self.start()
        partitions = self.consumer.partitions_for_topic(self.topic)
        logger.debug('Got list of partitions')
        result = len(partitions)
        if disabled:
            logger.debug('Consumers was not running, stop')
            await self.stop()
        return result

    async def fork(self) -> AnyKafkaConsumer:
        """Create copy of consumer and set it up"""
        child_consumer = self.__class__(self.bootstrap_servers,
                                        self.topic,
                                        self.group_id)
        await child_consumer.start()
        return child_consumer

    async def consume(self) -> GELFMessage:
        """Get another GELF message"""
        msg = await self.consumer.getone()
        value = msg.value.decode('utf-8')
        json_value = json.loads(value)
        message = GELFMessage(**json_value)
        return message
