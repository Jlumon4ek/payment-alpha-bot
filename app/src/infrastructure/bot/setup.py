from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from core.config import settings

def setup_bot():
    bot = Bot(token=settings.TOKEN)
    storage = RedisStorage.from_url(url=settings.REDIS)
    dp = Dispatcher(storage=storage)
    return bot, dp