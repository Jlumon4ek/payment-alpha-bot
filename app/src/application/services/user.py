from domain.models.user import User
from .base import BaseService

class UserService(BaseService):
    def __init__(self):
        super().__init__(User)

    async def get_by_telegram_id(self, telegram_id: int):
        return await self.get_by_field('telegram_id', telegram_id)

    async def create(self, telegram_id: int, username: str = None, full_name: str = None):
        return await super().create(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name
        )

    async def update(self, telegram_id: int, **kwargs):
        return await super().update('telegram_id', telegram_id, **kwargs)