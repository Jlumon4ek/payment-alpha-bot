from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


class SubscriptionKeyboard:
    async def subscription(self, type):
        builder = InlineKeyboardBuilder()

        kb = [
            types.InlineKeyboardButton(
                text="💳 Оплатить",
                callback_data=f"pay_{type}"
            ),
            types.InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data="backToStart"
            )   
        ]

        for button in kb:
            builder.row(button)

        return builder.as_markup()

    async def payment(self, type):
        builder = InlineKeyboardBuilder()

        kb = [
            types.InlineKeyboardButton(
                text="✅ Перейти к оплате",
                url="https://pay.kaspi.kz/pay/vrxmbs3d"
            ),
            types.InlineKeyboardButton(
                text="🧾 Я оплатил(а)",
                callback_data=f"paid_{type}"
            ),
            types.InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"backToSub_{type}"
            )
        ]

        for button in kb:
            builder.row(button)

        return builder.as_markup()

    async def backButton(self, type):
        builder = InlineKeyboardBuilder()

        kb = [
            types.InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"backToPay_{type}"
            )
        ]

        for button in kb:
            builder.row(button)

        return builder.as_markup()
    

    async def update_subscription(self):
        builder = InlineKeyboardBuilder()

        kb = [
            types.InlineKeyboardButton(
                text="🔄 Обновить подписку",
                callback_data="updateSubscription"
            )
        ]

        for button in kb:
            builder.row(button)

        return builder.as_markup()

subscription_keyboard = SubscriptionKeyboard()
