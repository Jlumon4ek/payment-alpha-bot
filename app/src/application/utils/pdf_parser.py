import re
from datetime import datetime
from PyPDF2 import PdfReader
from typing import Dict, Optional

import sentry_sdk

class PdfParser:    
    @staticmethod
    def extract_text(file_path: str) -> str:
        reader = PdfReader(file_path)
        return "".join(page.extract_text() for page in reader.pages)

    @staticmethod
    def extract_payment_data(text: str) -> Dict[str, any]:
        data = {}
                   
        match = re.search(r"(?:№ чека|Түбіртек №)\s*(.+)", text)
        if match:
            data["receipt_number"] = match.group(1).split("\n")[0].strip()
            
        customer_match = re.search(r"(?:ФИО покупателя|Сатып алушының аты-жөні)\s*(.+)", text)
        if customer_match:
            data["customer_name"] = customer_match.group(1).split("\n")[0].strip()
            
        iin_match = re.search(r"(?:ИИН/БИН продавца|Сатушының ЖСН/БСН)\s*(.+)", text)
        if iin_match:
            data["iin_bin"] = iin_match.group(1).split("\n")[0].strip()
        
        date_match = re.search(
            r'(?:Дата и время|Күні мен уақыты)\s*(?:по [\w\s]+)?([\d]{2}\.[\d]{2}\.[\d]{4} [\d]{2}:[\d]{2}(?::[\d]{2})?)',
            text
        )
        if date_match:
            data["payment_date"] = PdfParser._parse_date(date_match.group(1))
            
        price_match = re.search(r"(\d[\d\s]*)₸", text)
        if price_match:
            data["price"] = int(re.sub(r"\s", "", price_match.group(1)))
            
        return data

    @staticmethod
    def _parse_date(date_str: str) -> Optional[datetime]:
        try:
            return datetime.strptime(date_str, '%d.%m.%Y %H:%M:%S')
        except ValueError:
            try:
                return datetime.strptime(date_str, '%d.%m.%Y %H:%M')
            except ValueError as e:
                sentry_sdk.capture_exception(f"Error parsing date: {e}")
                return None