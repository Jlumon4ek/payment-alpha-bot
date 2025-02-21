# base.py
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

class BaseKeyboard:
    """
    Базовый класс для генерации inline-клавиатур.
    """
    def create_button(
        self,
        text: str,
        callback_data: str | None = None,
        url: str | None = None
    ) -> types.InlineKeyboardButton:
        """
        Создаёт одну кнопку с заданным текстом, callback_data или url.
        """
        return types.InlineKeyboardButton(
            text=text,
            callback_data=callback_data,
            url=url
        )

    def add_buttons(self, buttons: list[types.InlineKeyboardButton]) -> types.InlineKeyboardMarkup:
        """
        Принимает список кнопок, помещает каждую на свою строку
        и возвращает готовую клавиатуру.
        """
        builder = InlineKeyboardBuilder()
        for button in buttons:
            builder.row(button)
        return builder.as_markup()

    def back_button(self, callback_data: str) -> types.InlineKeyboardMarkup:
        """
        Создаёт клавиатуру с одной кнопкой "Назад".
        """
        button = self.create_button(
            text="⬅️ Назад",
            callback_data=callback_data
        )
        return self.add_buttons([button])
