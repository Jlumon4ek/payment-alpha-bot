from aiogram import Router, types
from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.admin.service import admin_service  

class AdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        telegram_id = message.from_user.id
        username = message.from_user.username
        full_name = message.from_user.full_name

        admin = await admin_service.get_by_telegram_id(telegram_id)

        if admin is not None:
            if admin.username != username or admin.full_name != full_name:
                await admin_service.update(telegram_id, username=username, full_name=full_name)
            return True  
        
        else:
            await message.answer(
                "You are not an admin. Please contact the admin for access."
            )
            return False