# subscription.py
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from .base import BaseKeyboard
from core.config import settings


class SubscriptionKeyboard(BaseKeyboard):
    SUBSCRIPTION_BUTTONS = [
        {"text": "💳 Оплатить", "callback_data": "pay_{type}"},
        {"text": "⬅️ Назад",   "callback_data": "backToStart"}
    ]

    PAYMENT_BUTTONS = [
        {"text": "✅ Перейти к оплате", "url": settings.PAYMENT_URL},
        {"text": "🧾 Я оплатил(а)",     "callback_data": "paid_{type}"},
        {"text": "⬅️ Назад",           "callback_data": "backToSub_{type}"}
    ]

    async def subscription(self) -> types.InlineKeyboardMarkup:
        return self._build_buttons(self.SUBSCRIPTION_BUTTONS, "month")

    async def payment(self) -> types.InlineKeyboardMarkup:
        return self._build_buttons(self.PAYMENT_BUTTONS, "month")

    async def backButton(self) -> types.InlineKeyboardMarkup:
        return self.back_button(f"backToPay_month")

    async def update_subscription(self) -> types.InlineKeyboardMarkup:

        button = self.create_button(
            text="🔄 Обновить подписку",
            callback_data="updateSubscription"
        )
        return self.add_buttons([button])

    def _build_buttons(self, config: list[dict], subscription_type: str) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for item in config:
            text = item["text"]
            callback_data = item.get("callback_data")
            url = item.get("url")

            if callback_data and "{type}" in callback_data:
                callback_data = callback_data.format(type=subscription_type)

            button = self.create_button(
                text=text,
                callback_data=callback_data,
                url=url
            )
            builder.row(button)

        return builder.as_markup()
