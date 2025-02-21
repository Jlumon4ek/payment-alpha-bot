# user.py
from .base import BaseKeyboard
from aiogram import types

class UserKeyboard(BaseKeyboard):
    async def start(self) -> types.InlineKeyboardMarkup:

        buttons = [
            self.create_button(
                text="Подписка на МЕСЯЦ",
                callback_data="subscription_month"
            )
        ]
        return self.add_buttons(buttons)
