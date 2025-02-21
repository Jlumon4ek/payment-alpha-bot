# src/presentation/filters/user.py
from aiogram.types import Message
from application.services.user import UserService
from .base import BaseUserFilter

class UserFilter(BaseUserFilter):
  
    def __init__(self):
        super().__init__(UserService())

    async def __call__(self, message: Message) -> bool:
        telegram_id = message.from_user.id
        username = message.from_user.username
        full_name = message.from_user.full_name

        user = await self.check_and_update_user(telegram_id, username, full_name)
        
        if user is None:
            await self.service.create(
                telegram_id,
                username=username,
                full_name=full_name
            )
            
        return True