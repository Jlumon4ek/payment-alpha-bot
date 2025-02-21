import asyncio
import logging
from aiogram.exceptions import TelegramServerError, TelegramNetworkError, TelegramAPIError
from aiogram import Bot, Dispatcher

class BotService:
    def __init__(self, bot: Bot, dp: Dispatcher, logger: logging.Logger):
        self.bot = bot
        self.dp = dp
        self.logger = logger
        self.retry_attempts = 5

    async def start(self, router_list):
        self.dp.include_routers(*router_list)
        
        for attempt in range(self.retry_attempts):
            try:
                self.logger.info("Start polling")
                await self.dp.start_polling(self.bot)
                break
            except TelegramNetworkError as e:
                self.logger.error(f"Network error: {e}")
                await self._handle_error(attempt)
            except TelegramAPIError as e:
                self.logger.error(f"API error: {e}")
                await self._handle_error(attempt)
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                await self._handle_error(attempt)
        else:
            self.logger.error("Max retry attempts reached. Could not start bot.")

    async def _handle_error(self, attempt: int):
        await asyncio.sleep(2 ** attempt)