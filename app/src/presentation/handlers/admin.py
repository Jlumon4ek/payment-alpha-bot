from aiogram import Router, types, Bot
from aiogram.filters import Command, CommandObject
from core.config import settings
from application.filters.admin import AdminFilter

router = Router()
bot = Bot(token=settings.TOKEN)

class AdminHandlers:
    def __init__(self, router: Router):
        self.router = router
        self.setup_handlers()

    def setup_handlers(self):
        self.router.message.register(self.logs, Command("logs"), AdminFilter())
        self.router.message.register(self.membercount, Command("membercount"), AdminFilter())
        self.router.message.register(self.banwave, Command("banwave"), AdminFilter())

    async def logs(self, message: types.Message, command: CommandObject):
        await message.answer("Логи")

    async def membercount(self, message: types.Message, command: CommandObject):
        chat_count = await bot.get_chat_member_count(settings.CHANNEL_ID)
        await message.answer(f"Количество участников в канале: {chat_count}")

    async def banwave(self, message: types.Message, command: CommandObject):
        await message.answer("Бан вейв начался")

admin_handlers = AdminHandlers(router)
