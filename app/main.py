from contextlib import asynccontextmanager
from pathlib import Path
from config import settings
from aiogram import Bot, Dispatcher
from aiogram.types import Update
import logging
from aiogram.fsm.storage.redis import RedisStorage
from constants import router_list
from aiogram.exceptions import TelegramServerError, TelegramNetworkError, TelegramAPIError
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=settings.TOKEN)
dp = Dispatcher()
storage = RedisStorage.from_url(url=settings.REDIS)


async def main():
    dp.include_routers(*router_list)

    retry_attempts = 5
    for attempt in range(retry_attempts):
        try:
            logger.info("Start polling")
            await dp.start_polling(bot)
            break
        except TelegramNetworkError as e:
            logger.error(f"Network error: {e}")
            await asyncio.sleep(2 ** attempt)
        except TelegramAPIError as e:
            logger.error(f"API error: {e}")
            await asyncio.sleep(2 ** attempt)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            await asyncio.sleep(2 ** attempt)
    else:
        logger.error("Max retry attempts reached. Could not start bot.")

if __name__ == "__main__":
    asyncio.run(main())