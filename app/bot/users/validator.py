from aiogram.filters import BaseFilter
from aiogram.types import Message
from bot.users.service import user_service

class UserFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        telegram_id = message.from_user.id
        username = message.from_user.username
        full_name = message.from_user.full_name

        user = await user_service.get_by_telegram_id(telegram_id)

        if user is not None:
            if user.username != username or user.full_name != full_name:
                await user_service.update(telegram_id, username=username, full_name=full_name)
        
        else:
            await user_service.create(telegram_id, username=username, full_name=full_name)
            
        return True

