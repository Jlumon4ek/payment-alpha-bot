from aiogram import Router, types, Bot, F
from aiogram.fsm.context import FSMContext
from core.config import settings
from datetime import datetime, timedelta
from application.filters.user import UserFilter
from presentation.keyboards.subscription import SubscriptionKeyboard
from application.states.subscription import SendReceipt
from application.services.subscription import SubscriptionService
from application.utils.receipt_handler import ReceiptHandler

router = Router()
bot = Bot(token=settings.TOKEN)
subscription_keyboard = SubscriptionKeyboard()
subscription_service = SubscriptionService()
receipt_handler = ReceiptHandler()

class SubscriptionHandlers:
    def __init__(self, router: Router):
        self.router = router
        self.setup_handlers()

    def setup_handlers(self):
        self.router.callback_query.register(
            self.subscription_handler,
            F.data.in_({"subscription_month", "subscription_day", "backToSub_day", "backToSub_month"}),
            UserFilter()
        )
        self.router.callback_query.register(
            self.pay_handler,
            F.data.in_({"pay_month", "pay_day", "backToPay_month", "backToPay_day"}),
            UserFilter()
        )
        self.router.callback_query.register(
            self.paid_handler,
            F.data.in_({"paid_month", "paid_day"}),
            UserFilter()
        )
        self.router.message.register(
            self.send_receipt_handler,
            SendReceipt.receipt
        )

    @staticmethod
    def get_subscription_details(subscription_type: str) -> tuple[int, str]:
        if subscription_type == "month":
            return 1490, "30 дней"
        return 499, "1 день"

    async def subscription_handler(self, callback: types.CallbackQuery):
        await callback.answer()
        subscription_type = callback.data.split("_")[1]
        price, duration = self.get_subscription_details(subscription_type)
        
        await callback.message.answer(
            f"Срок подписки: {duration}\n\nСтоимость: {price} тг.",
            reply_markup=await subscription_keyboard.subscription(subscription_type)
        )

    async def pay_handler(self, callback: types.CallbackQuery):
        await callback.answer()
        subscription_type = callback.data.split("_")[1]
        price, duration = self.get_subscription_details(subscription_type)
        
        await callback.message.answer(
            f"Срок подписки: {duration}\n\nСтоимость: {price} тг.",
            reply_markup=await subscription_keyboard.payment(subscription_type)
        )

    async def paid_handler(self, callback: types.CallbackQuery, state: FSMContext):
        await callback.answer()
        subscription_type = callback.data.split("_")[1]
        
        await callback.message.answer(
            "Төлемді растайтын құжатты PDF форматында жіберуіңізді өтінеміз.\n\n"
            "Пожалуйста, отправьте квитанцию о платеже в формате PDF.",
            reply_markup=await subscription_keyboard.backButton(subscription_type)
        )
        await state.update_data(subscription_type=subscription_type)
        await state.set_state(SendReceipt.receipt)

    async def send_receipt_handler(self, message: types.Message, state: FSMContext):
        data = await state.get_data()
        subscription_type = data.get("subscription_type")

        check_result, data = await receipt_handler.checkPdf(
            file_id=message.document.file_id,
            subscription_type=subscription_type,
            telegram_id=message.from_user.id
        )

        if check_result:
            try:
                await bot.unban_chat_member(
                    chat_id=settings.CHANNEL_ID,
                    user_id=message.from_user.id
                )
            except Exception:
                pass

            channel_link = await bot.create_chat_invite_link(
                settings.CHANNEL_ID,
                member_limit=1
            )

            await message.answer(
                "Міне, сіздің бір реттік сілтемеңіз. Оны басқаларға жібермеңіз.\n\n"
                "Вот ваша одноразовая ссылка. Не отправляйте ее третьим лицам.\n\n"
                f"{channel_link.invite_link}"
            )
        else:
            await message.answer(data)

        await state.clear()

subscription_handlers = SubscriptionHandlers(router)