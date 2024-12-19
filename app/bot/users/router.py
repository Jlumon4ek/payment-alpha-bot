from aiogram import (
    F,
    types,
    Bot,
    Router
)
from aiogram.fsm.context import FSMContext
from config import settings
from datetime import datetime
from aiogram.filters import Command, CommandObject
from bot.users.keyboard import user_keyboard
from bot.users.validator import UserFilter

bot = Bot(token=settings.TOKEN)

router = Router()

@router.message(Command("start"), UserFilter())
async def start(message: types.Message, command: CommandObject):
    await message.answer(
        "Сәлеметсіз бе! Тарифты таңдаңыз.\n\nЗдравствуйте! Выберите тариф.",
        reply_markup=await user_keyboard.start()
    )

@router.callback_query(F.data.in_({"backToStart", "updateSubscription"}), UserFilter())
async def back_to_start(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "Сәлеметсіз бе! Тарифты таңдаңыз.\n\nЗдравствуйте! Выберите тариф.",
        reply_markup=await user_keyboard.start()
    )