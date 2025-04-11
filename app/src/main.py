import asyncio
from infrastructure.logging.setup import setup_logging, setup_sentry
from infrastructure.bot.setup import setup_bot
from application.bot_service import BotService
from core.constants import router_list
from core.config import settings
import sentry_sdk

async def main():

    logger = setup_logging()

    if settings.SENTRY_DSN:
        setup_sentry(
            dsn=settings.SENTRY_DSN, 
        )

    bot, dp = setup_bot()
    
    bot_service = BotService(bot, dp, logger)
    await bot_service.start(router_list)

if __name__ == "__main__":
    asyncio.run(main())