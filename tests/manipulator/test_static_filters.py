from critical.manipulator.static_filters import SourceIPFilter
from critical.manipulator.static_filters import MessageBodyFilter
from critical.manipulator.static_filters import MessageBodyAnyFilter


def test_source_ip_filter(composer):
    current_filter = SourceIPFilter(ips=['127.0.0.1'])
    message_include = composer.message(ip_address='127.0.0.1')
    message_exclude = composer.message(ip_address='127.0.0.2')
    assert current_filter.filter(message_include) is True
    assert current_filter.filter(message_exclude) is False

    current_filter = SourceIPFilter(ips=['127.0.0.1', '127.0.0.2'])
    message_include_1 = composer.message(ip_address='127.0.0.1')
    message_include_2 = composer.message(ip_address='127.0.0.2')
    message_exclude = composer.message(ip_address='127.0.0.3')
    assert current_filter.filter(message_include_1) is True
    assert current_filter.filter(message_include_2) is True
    assert current_filter.filter(message_exclude) is False

    current_filter = SourceIPFilter(prefixes=['127.0.0.0/8'])
    message_include_1 = composer.message(ip_address='127.0.0.1')
    message_include_2 = composer.message(ip_address='127.0.0.2')
    message_exclude = composer.message(ip_address='10.10.10.10')
    assert current_filter.filter(message_include_1) is True
    assert current_filter.filter(message_include_2) is True
    assert current_filter.filter(message_exclude) is False

    current_filter = SourceIPFilter(ips=['127.0.0.1'], exclude=True)
    message_include = composer.message(ip_address='127.0.0.2')
    message_exclude = composer.message(ip_address='127.0.0.1')
    assert current_filter.filter(message_include) is True
    assert current_filter.filter(message_exclude) is False

    current_filter = SourceIPFilter(prefixes=['127.0.0.0/8'], exclude=True)
    message_include_1 = composer.message(ip_address='10.10.10.10')
    message_include_2 = composer.message(ip_address='192.168.0.1')
    message_exclude_1 = composer.message(ip_address='127.0.0.1')
    message_exclude_2 = composer.message(ip_address='127.0.0.2')
    assert current_filter.filter(message_include_1) is True
    assert current_filter.filter(message_include_2) is True
    assert current_filter.filter(message_exclude_1) is False
    assert current_filter.filter(message_exclude_2) is False


def test_message_body_filter(composer):
    current_filter = MessageBodyFilter(pattern='text')
    message_include = composer.message(short='message with good text')
    message_exclude = composer.message(short='message with nothing')
    assert current_filter.filter(message_include) is True
    assert current_filter.filter(message_exclude) is False

    current_filter = MessageBodyFilter(pattern='text', exclude=True)
    message_include = composer.message(short='message with nothing')
    message_exclude = composer.message(short='message with bad text')
    assert current_filter.filter(message_include) is True
    assert current_filter.filter(message_exclude) is False


def test_message_body_any_filter(composer):
    current_filter = MessageBodyAnyFilter(patterns=['one', 'two', 'three'])
    message_include_1 = composer.message(short='message with one')
    message_include_2 = composer.message(short='message with two')
    message_include_3 = composer.message(short='message with three')
    message_exclude = composer.message(short='message with nothing good')
    assert current_filter.filter(message_include_1) is True
    assert current_filter.filter(message_include_2) is True
    assert current_filter.filter(message_include_3) is True
    assert current_filter.filter(message_exclude) is False

    current_filter = MessageBodyAnyFilter(patterns=['one', 'two', 'three'],
                                          exclude=True)
    message_include = composer.message(short='message with nothing bad')
    message_exclude_1 = composer.message(short='message with one')
    message_exclude_2 = composer.message(short='message with two')
    message_exclude_3 = composer.message(short='message with three')
    assert current_filter.filter(message_include) is True
    assert current_filter.filter(message_exclude_1) is False
    assert current_filter.filter(message_exclude_2) is False
    assert current_filter.filter(message_exclude_3) is False
