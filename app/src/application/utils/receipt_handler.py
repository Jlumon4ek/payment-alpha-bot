import os
from datetime import datetime, timedelta
from aiogram import Bot
from core.config import settings
from application.services.subscription import SubscriptionService, PaymentService
from .pdf_parser import PdfParser

class ReceiptHandler:
    def __init__(self):
        self.bot = Bot(token=settings.TOKEN)
        self.subscription_service = SubscriptionService()
        self.pdf_parser = PdfParser()
        self.payment_service = PaymentService()  

    async def checkPdf(self, file_id: str, subscription_type: str, telegram_id: int):
        file_path = f"{file_id}.pdf"
        
        try:
            file_info = await self.bot.get_file(file_id)
            downloaded_file = await self.bot.download_file(file_info.file_path)
            
            with open(file_path, "wb") as file:
                file.write(downloaded_file.read())

            text = self.pdf_parser.extract_text(file_path)
            data = self.pdf_parser.extract_payment_data(text)

            validation_result = await self._validate_payment_data(
                data, subscription_type, telegram_id
            )
            if not validation_result[0]:
                return validation_result

            await self._create_subscription_records(
                data, subscription_type, telegram_id
            )

            return True

        except Exception as e:
            return False
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    async def _validate_payment_data(self, data: dict, subscription_type: str, telegram_id: int):
        # if "payment_date" in data:
        #     current_month = datetime.now().month
        #     if data["payment_date"].month != current_month:
        #         return False, "Дата платежа не соответствует текущему месяцу."

        if "price" in data:
            min_price = 1490 if subscription_type == "month" else 499
            if data["price"] < min_price:
                return False, f"Неверная сумма платежа. Минимальная сумма: {min_price} тг."

        if "receipt_number" in data:
            existing_receipt = await self.payment_service.get_by_receipt_id(data["receipt_number"])
            if existing_receipt:
                return False, "Квитанция с таким номером уже существует."

        return True, None

    async def _create_subscription_records(self, data: dict, subscription_type: str, telegram_id: int):
        await self.subscription_service.add_payment(
            telegram_id=telegram_id,
            receipt_id=data['receipt_number'],
            full_name=data['customer_name'],
            passport_id=data['iin_bin'],
            price=data['price'],
            payment_date=datetime.now()
        )

        current_subscription = await self.subscription_service.get_subscription_by_telegram_id(telegram_id)
        
        current_time = datetime.now()
        extension_period = timedelta(days=30 if subscription_type == "month" else 1)
        new_end_date = current_time + extension_period

        if current_subscription:
            if current_subscription.isActive:
                new_end_date = max(
                    current_subscription.subscription_end,
                    current_time
                ) + extension_period
                new_start_date = current_subscription.subscription_start
            else:
                new_start_date = current_time
            
            await self.subscription_service.update(
                field_name='telegram_id',
                field_value=telegram_id,
                subscription_start=new_start_date,
                subscription_end=new_end_date,
                subscription_price=data['price'],
                isActive=True,
                subscription_type=subscription_type,
                notified_24 = False,
                notified_1 = False
            )
        else:
            await self.subscription_service.create(
                telegram_id=telegram_id,
                subscription_type=subscription_type,
                subscription_start=current_time,
                subscription_end=new_end_date,
                subscription_price=data['price']
            )