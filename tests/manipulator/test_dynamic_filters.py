import pytest

from critical.manipulator.dynamic_filters import RedisExcludeRegexp


@pytest.mark.asyncio
async def test_redis_exclude_regexp(composer, redis_creds):
    current_filter = RedisExcludeRegexp(**redis_creds)
    assert current_filter.redis is None
    await current_filter.start()
    assert current_filter.redis is not None

    key = 'test_key'

    await current_filter.redis.sadd(key, r'\d{3}')
    message_include = 'message that contains three numbers 123'
    message_exclude = 'message that contains nothing bad'
    assert await current_filter.filter(message_include, key) is True
    assert await current_filter.filter(message_exclude, key) is False
    await current_filter.redis.srem('test_key', 'test_value')

    await current_filter.redis.sadd(key, r'inva[lid')
    message_include = 'message that contains inva[lid regexp'
    message_exclude = 'message that contains nothing bad'
    assert await current_filter.filter(message_include, key) is True
    assert await current_filter.filter(message_exclude, key) is False
    await current_filter.redis.srem('test_key', 'test_value')

    await current_filter.stop()
    assert current_filter.redis is None
