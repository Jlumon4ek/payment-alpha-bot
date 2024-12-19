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
from bot.admin.validator import AdminFilter

bot = Bot(token=settings.TOKEN)

router = Router()


@router.message(Command("logs"), AdminFilter())
async def logs(message: types.Message, command: CommandObject):
    await message.answer(
        "Логи"
    )

@router.message(Command("membercount"), AdminFilter())
async def membercount(message: types.Message, command: CommandObject):
    chat = await bot.get_chat_member_count(settings.CHANNEL_ID)
    await message.answer(
        f"Количество участников в канале: {chat}"
    )

@router.message(Command("banwave"), AdminFilter())
async def banwave(message: types.Message, command: CommandObject):
    await message.answer(
        "Бан вейв начался"
    )