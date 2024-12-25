from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime
from config import settings


class UserKeyboard:
    async def start(self):
        builder = InlineKeyboardBuilder()

        kb = [
            types.InlineKeyboardButton(
                text="Подписка на МЕСЯЦ",
                callback_data="subscription_month"
            ),
            # types.InlineKeyboardButton(
            #     text="Подписка на ДЕНЬ",
            #     callback_data="subscription_day"
            # )   
        ]

        for button in kb:
            builder.row(button)

        return builder.as_markup()


user_keyboard = UserKeyboard()