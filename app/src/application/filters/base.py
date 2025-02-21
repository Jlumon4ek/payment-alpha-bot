# src/presentation/filters/base.py
from aiogram.filters import BaseFilter
from aiogram.types import Message
from application.services.base import BaseService

class BaseUserFilter(BaseFilter):
    
    def __init__(self, service: BaseService):
        self.service = service

    async def check_and_update_user(self, telegram_id: int, username: str, full_name: str) -> None:
        user = await self.service.get_by_telegram_id(telegram_id)

        if user is not None:
            if user.username != username or user.full_name != full_name:
                await self.service.update(
                    telegram_id,
                    username=username,
                    full_name=full_name
                )
            return user
        return None