from aiogram.types import Message
from application.services.admin import AdminService
from .base import BaseUserFilter

class AdminFilter(BaseUserFilter):   
    def __init__(self):
        super().__init__(AdminService())

    async def __call__(self, message: Message) -> bool:
        telegram_id = message.from_user.id
        username = message.from_user.username
        full_name = message.from_user.full_name

        admin = await self.check_and_update_user(telegram_id, username, full_name)
        
        if admin is not None:
            return True
        
        await message.answer(
            "You are not an admin. Please contact the admin for access."
        )
        return False