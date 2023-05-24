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
                      DummyFormatter(), [DummySender([None])])
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
                     'receivers': [None]}]
    }
    handler = Handler.from_dict(valid_dict.copy())
    logging.error(valid_dict)

    invalid_dict_formatter = valid_dict = {
        'formatter': {'class': 'InvalidClass'},
        'static_filters': [{'class': 'DummyStaticFilter'}],
        'dynamic_filters': [{'class': 'DummyDynamicFilter'}],
        'senders': [{'class': 'DummySender',
                     'receivers': [None]}]
    }
    with pytest.raises(AttributeError):
        handler = Handler.from_dict(invalid_dict_formatter)

    invalid_dict_static_filter = valid_dict = {
        'formatter': {'class': 'DummyFormatter'},
        'static_filters': [{'class': 'InvalidClass'}],
        'dynamic_filters': [{'class': 'DummyDynamicFilter'}],
        'senders': [{'class': 'DummySender',
                     'receivers': [None]}]
    }
    with pytest.raises(AttributeError):
        handler = Handler.from_dict(invalid_dict_static_filter)

    invalid_dict_dynamic_filters = valid_dict = {
        'formatter': {'class': 'DummyFormatter'},
        'static_filters': [{'class': 'DummyStaticFilter'}],
        'dynamic_filters': [{'class': 'InvalidClass'}],
        'senders': [{'class': 'DummySender',
                     'receivers': [None]}]
    }
    with pytest.raises(AttributeError):
        handler = Handler.from_dict(invalid_dict_dynamic_filters)

    invalid_dict_sender = valid_dict = {
        'formatter': {'class': 'DummyFormatter'},
        'static_filters': [{'class': 'DummyStaticFilter'}],
        'dynamic_filters': [{'class': 'DummyDynamicFilter'}],
        'senders': [{'class': 'InvalidClass',
                     'receivers': [None]}]
    }
    with pytest.raises(AttributeError):
        handler = Handler.from_dict(invalid_dict_sender)
