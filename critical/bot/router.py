from aiogram import Router, types, flags, F
from aiogram.filters import CommandObject
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
import redis.asyncio as redis

router = Router()


@router.message(Command(commands=['filter']))
@flags.is_using_redis
async def add_pattern(message: types.Message,
                      command: CommandObject,
                      redis_instance: redis.Redis):
    key = f'tg_{message.chat.id}'
    pattern = command.args
    result = await redis_instance.sadd(key, pattern)
    if not result:
        await message.reply('Already ignored')
    else:
        await message.reply(f'Will be ignored from now')


@router.message(Command(commands=['delete']))
@flags.is_using_redis
async def remove_pattern(message: types.Message,
                         command: CommandObject,
                         redis_instance: redis.Redis):
    key = f'tg_{message.chat.id}'
    pattern = command.args
    result = await redis_instance.srem(key, pattern)
    if not result:
        await message.reply('Already not ignored')
    else:
        await message.reply('Will not be ignored from now')


@router.message(Command(commands=['show']))
@flags.is_using_redis
async def show(message: types.Message,
               redis_instance: redis.Redis):
    key = f'tg_{message.chat.id}'
    patterns = await redis_instance.smembers(key)
    if not patterns:
        await message.reply('Nothing is ignored in this chat')
    else:
        text = 'Ignored patterns:\n'
        for index, pattern in enumerate(patterns):
            text += str(index+1) + '. ' + pattern + '\n'
        await message.answer(text)


@router.message(F.text.contains(' бот'))
@router.message(F.text.contains(' bot'))
async def react(message: types.Message):
    await message.reply('Please don\'t mention me without urge need. '
                        'Use commands instead')
