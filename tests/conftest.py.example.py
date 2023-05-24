import faker
import datetime
import pytest

from critical.manipulator.models import GELFMessage


@pytest.fixture
def composer():
    return MessageComposer()


@pytest.fixture
def kafka_creds():
    return {'bootstrap_servers': '127.0.0.1',
            'topic': 'test-critical',
            'group_id': 'test-critical.test'}


@pytest.fixture
def redis_creds():
    return {'host': '127.0.0.1',
            'db': 0}


@pytest.fixture
def telegram_token():
    return '1234567890:AAAAAbbbbbCddEEff0HiiJJJJ1K-L2mmmmN'


@pytest.fixture
def telegram_chat_id():
    return '123456789'

class MessageComposer:
    def __init__(self):
        self.fake = faker.Faker()
        faker.Faker.seed(0)

    def message(self, hostname: str = None,
                short: str = None,
                ip_address: str = None):
        fake_hostname = hostname or self.fake.hostname()
        fake_sentence = short or self.fake.sentence()
        fake_short = fake_sentence
        fake_datetime = datetime.datetime. \
            now(). \
            replace(tzinfo=datetime.timezone.utc)
        fake_long = '<190>' + fake_datetime.strftime('%Y-%m-%d %H:%M:%S') + ' '
        fake_long += fake_hostname + ' ' + fake_short
        msg_dict = {"version": "1.1",
                    "timestamp": int(fake_datetime.timestamp()),
                    "host": fake_hostname,
                    "short_message": fake_short,
                    "level": 6,
                    "full_message": fake_long,
                    "_level": 6,
                    "_gl2_remote_ip": ip_address or self.fake.ipv4(),
                    "_gl2_remote_port": 33333,
                    "_gl2_message_id": "OSHEIN4AICHIBUI1IO0IEWEIRA",
                    "_kafka_topic": "test-critical",
                    "_source": fake_hostname,
                    "_message": fake_short,
                    "_gl2_source_input": "0123456789abcdef01234567",
                    "_full_message": fake_long,
                    "_facility_num": 23,
                    "_forwarder": "org.graylog2.outputs.GelfOutput",
                    "_gl2_source_node": self.fake.uuid4(),
                    "_id": self.fake.uuid4(),
                    "_facility": "local7",
                    "_timestamp": fake_datetime.isoformat()}
        return GELFMessage(**msg_dict)
