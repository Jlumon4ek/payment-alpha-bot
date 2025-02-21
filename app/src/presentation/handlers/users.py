# src/presentation/handlers/user.py
from aiogram import Router, types, Bot, F
from aiogram.filters import Command, CommandObject
from core.config import settings
from application.filters.user import UserFilter
from presentation.keyboards.user import UserKeyboard

router = Router()
bot = Bot(token=settings.TOKEN)
user_keyboard = UserKeyboard()

class UserHandlers:
    def __init__(self, router: Router):
        self.router = router
        self.setup_handlers()

    def setup_handlers(self):
        self.router.message.register(self.start, Command("start"), UserFilter())
        self.router.callback_query.register(
            self.back_to_start,
            F.data.in_({"backToStart", "updateSubscription"}),
            UserFilter()
        )

    async def start(self, message: types.Message, command: CommandObject):
        await message.answer(
            "Сәлеметсіз бе! Тарифты таңдаңыз.\n\n"
            "Здравствуйте! Выберите тариф.",
            reply_markup=await user_keyboard.start()
        )

    async def back_to_start(self, callback: types.CallbackQuery):
        await callback.answer()
        await callback.message.answer(
            "Сәлеметсіз бе! Тарифты таңдаңыз.\n\n"
            "Здравствуйте! Выберите тариф.",
            reply_markup=await user_keyboard.start()
        )



user_handlers = UserHandlers(router)