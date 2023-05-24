import logging

import pytest

from critical.manipulator.handler import Handler
from critical.manipulator.formatters import DummyFormatter
from critical.manipulator.static_filters import DummyStaticFilter
from critical.manipulator.dynamic_filters import DummyDynamicFilter
from critical.manipulator.senders import DummySender


@pytest.mark.asyncio
async def test_handler(composer):
    handler = Handler([DummyStaticFilter(True)], [DummyDynamicFilter()],
                      DummyFormatter(), [DummySender([None])], 'consumer_spec')
    await handler.start()
    gelf = composer.gelf()
    await handler.handle(gelf)
    handler.static_filters = [DummyStaticFilter(False)]
    await handler.handle(gelf)
    await handler.stop()

    valid_dict = {
        'formatter': {'class': 'DummyFormatter'},
        'static_filters': [{'class': 'DummyStaticFilter'}],
        'dynamic_filters': [{'class': 'DummyDynamicFilter'}],
        'senders': [{'class': 'DummySender',
                     'receivers': [None]}],
        'name': 'Test Handler',
        'consumer_specification': 'consumer_spec'
    }
    handler = Handler.from_dict(valid_dict.copy())
    logging.error(valid_dict)

    invalid_dict_formatter = {
        'formatter': {'class': 'InvalidClass'},
        'static_filters': [{'class': 'DummyStaticFilter'}],
        'dynamic_filters': [{'class': 'DummyDynamicFilter'}],
        'senders': [{'class': 'DummySender',
                     'receivers': [None]}],
        'consumer_specification': 'consumer_spec'
    }
    with pytest.raises(AttributeError):
        handler = Handler.from_dict(invalid_dict_formatter)

    invalid_dict_static_filter = {
        'formatter': {'class': 'DummyFormatter'},
        'static_filters': [{'class': 'InvalidClass'}],
        'dynamic_filters': [{'class': 'DummyDynamicFilter'}],
        'senders': [{'class': 'DummySender',
                     'receivers': [None]}],
        'consumer_specification': 'consumer_spec'
    }
    with pytest.raises(AttributeError):
        handler = Handler.from_dict(invalid_dict_static_filter)

    invalid_dict_dynamic_filters = {
        'formatter': {'class': 'DummyFormatter'},
        'static_filters': [{'class': 'DummyStaticFilter'}],
        'dynamic_filters': [{'class': 'InvalidClass'}],
        'senders': [{'class': 'DummySender',
                     'receivers': [None]}],
        'consumer_specification': 'consumer_spec'
    }
    with pytest.raises(AttributeError):
        handler = Handler.from_dict(invalid_dict_dynamic_filters)

    invalid_dict_sender = {
        'formatter': {'class': 'DummyFormatter'},
        'static_filters': [{'class': 'DummyStaticFilter'}],
        'dynamic_filters': [{'class': 'DummyDynamicFilter'}],
        'senders': [{'class': 'InvalidClass',
                     'receivers': [None]}],
        'consumer_specification': 'consumer_spec'
    }
    with pytest.raises(AttributeError):
        handler = Handler.from_dict(invalid_dict_sender)
