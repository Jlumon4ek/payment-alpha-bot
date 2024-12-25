import re
from PyPDF2 import PdfReader
import os
from aiogram import (
    Bot
)
from config import settings
from bot.subscription.service import subscription_service
from datetime import datetime, timedelta


bot = Bot(token=settings.TOKEN)

class SubscriptionHandler:
    async def checkPdf(self, file_id, subscription_type, telegram_id):
        file_info = await bot.get_file(file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        
        data = {}

        file_path = f"{file_id}.pdf"
        with open(file_path, "wb") as file:
            file.write(downloaded_file.read())

        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()

            if settings.COMPANY_NAME in text:
                data["store_name"] = settings.COMPANY_NAME
            if "№ чека" in text:
                data["receipt_number"] = text.split("№ чека")[1].split("\n")[0].strip()
            if "ФИО покупателя" in text:
                data["customer_name"] = text.split("ФИО покупателя")[1].split("\n")[0].strip()
            if "ИИН/БИН продавца" in text:
                data["iin_bin"] = text.split("ИИН/БИН продавца")[1].split("\n")[0].strip()
            date_match = re.search(r'Дата и время\s*(?:по [\w\s]+)?([\d\.\: ]+)', text)

            if date_match:
                data["payment_date"] = date_match.group(1)

                date_time_str = date_match.group(1)
                date_time = datetime.strptime(date_time_str, '%d.%m.%Y %H:%M:%S')
                current_month = datetime.now().month
                if date_time.month != current_month:
                    return False, "Дата платежа не соответствует текущему месяцу. Пожалуйста, проверьте дату платежа."
            
            price_match = re.search(r"(\d[\d\s]*)₸", text)
            if price_match:
                data["price"] = int(re.sub(r"\s", "", price_match.group(1)))

            if subscription_type == "month":
                if data["price"] < 1490:
                    return False, f"Неверная сумма платежа. Сумма должна быть не менее 1490 тг. Ваша сумма {data['price']}"
                
            if subscription_type == "day":
                if data["price"] < 499: 
                    return False, f"Неверная сумма платежа. Сумма должна быть не менее 499 тг. Ваша сумма {data['price']}"             
                
            receipt = await subscription_service.get_payment(data['receipt_number'])

            if receipt is not None:
                return False, "Квитанция с таким номером уже существует. "


            await subscription_service.add_payment(
                telegram_id=telegram_id,
                store_name=data['store_name'],
                receipt_id=data['receipt_number'],
                full_name=data['customer_name'],
                passport_id=data['iin_bin'],
                price=data['price'],
                payment_date = datetime.now()
            )

            # activeSub = await subscription_service.get_active_subscription(telegram_id)

            # if activeSub is not None:
            #     subscription_end = activeSub.subscription_end
            # else:
            subscription_end = datetime.now()
            
            if subscription_type == "month":
                subscription_end += timedelta(days=30)
            elif subscription_type == "day":
                subscription_end += timedelta(hours=24)

            # if activeSub is not None:
            #     await subscription_service.update_subscription(
            #         subscription_id = activeSub.id,
            #         subscription_end = subscription_end,
            #         subscription_price=activeSub.subscription_price + data['price']
            #     )
            # else:
            await subscription_service.add_subscription(
                telegram_id=telegram_id,
                subscription_type=subscription_type,
                subscription_end=subscription_end,
                subscription_price=data['price'],
                
            )  
            
            return True, data
                    
        except Exception as e:
            return False, f"Ошибка при обработке файла. {e}"


        
        finally:
            os.remove(file_path)
    
        

receipt_handler = SubscriptionHandler()