import os
from aiogram import (
    F,
    types,
    Bot,
    Router
)
from aiogram.fsm.context import FSMContext
from config import settings
from datetime import datetime, timedelta
from aiogram.filters import Command, CommandObject
from bot.subscription.keyboard import subscription_keyboard
from bot.subscription.state import SendReceipt
from aiogram.types import ChatInviteLink
from bot.subscription.utills import receipt_handler
from bot.subscription.service import subscription_service
from bot.users.validator import UserFilter

bot = Bot(token=settings.TOKEN)

router = Router()



@router.callback_query(F.data.in_({"subscription_month", "subscription_day", "backToSub_day", "backToSub_month"}), UserFilter())
async def subscription_month(callback: types.CallbackQuery):
    await callback.answer()
    
    subcscription_type = callback.data.split("_")[1]
    button = await subscription_keyboard.subscription(subcscription_type)

    if subcscription_type == "month":
        subscription_price = 1490
        subscription_duration = "30 дней"
    if subcscription_type == "day":
        subscription_price = 499
        subscription_duration = "1 день"
    
    await callback.message.answer(
        f"Срок подписки: {subscription_duration}\n\nСтоимость: {subscription_price} тг.",
        reply_markup=button
    )

@router.callback_query(F.data.in_({"pay_month", "pay_day", "backToPay_month", "backToPay_day"}), UserFilter())
async def pay(callback: types.CallbackQuery):
    await callback.answer()

    subcscription_type = callback.data.split("_")[1]

    button = await subscription_keyboard.payment(subcscription_type)

    if subcscription_type == "month":
        subscription_price = 1490
        subscription_duration = "30 дней"
    if subcscription_type == "day":
        subscription_price = 499
        subscription_duration = "1 день"
    
    await callback.message.answer(
        f"Срок подписки: {subscription_duration}\n\nСтоимость: {subscription_price} тг.",
        reply_markup=button
    )

@router.callback_query(F.data.in_({"paid_month", "paid_day"}), UserFilter())
async def paid(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    subcscription_type = callback.data.split("_")[1]

    button = await subscription_keyboard.backButton(subcscription_type)

    await callback.message.answer(
        "Төлемді растайтын құжатты PDF форматында жіберуіңізді өтінеміз.\n\nПожалуйста, отправьте квитанцию о платеже в формате PDF.",
        reply_markup=button
    )
    await state.update_data(subscription_type=subcscription_type)
    await state.set_state(SendReceipt.receipt)
    
    
@router.message(SendReceipt.receipt)
async def send_receipt(message: types.Message, state: FSMContext):
    data = await state.get_data()

    subscription_type = data.get("subscription_type")

    checkPdfResult, data = await receipt_handler.checkPdf(
        file_id = message.document.file_id,
        subscription_type = subscription_type,
        telegram_id=message.from_user.id
    )

    if checkPdfResult == True:      
        channel_id = settings.CHANNEL_ID

        try:
            await bot.unban_chat_member(
                chat_id=channel_id,
                user_id=message.from_user.id
            )
        except Exception as e:
            pass
        
        channel_link = await bot.create_chat_invite_link(
            channel_id,
            member_limit=1
        )

        await message.answer(f"Міне, сіздің бір реттік сілтемеңіз. Оны басқаларға жібермеңіз.\n\nВот ваша одноразовая ссылка. Не отправляйте ее третьим лицам.\n\n{channel_link.invite_link}")

    else:
        await message.answer(data)
    
    await state.clear()

