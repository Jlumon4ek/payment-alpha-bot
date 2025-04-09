import re
from datetime import datetime
from PyPDF2 import PdfReader
from typing import Dict, Optional

class PdfParser:    
    @staticmethod
    def extract_text(file_path: str) -> str:
        reader = PdfReader(file_path)
        return "".join(page.extract_text() for page in reader.pages)

    @staticmethod
    def extract_payment_data(text: str) -> Dict[str, any]:
        data = {}
                   
        if "№ чека" in text:
            data["receipt_number"] = text.split("№ чека")[1].split("\n")[0].strip()
            
        if "ФИО покупателя" in text:
            data["customer_name"] = text.split("ФИО покупателя")[1].split("\n")[0].strip()
            
        if "ИИН/БИН продавца" in text:
            data["iin_bin"] = text.split("ИИН/БИН продавца")[1].split("\n")[0].strip()
            
        date_match = re.search(
            r'Дата и время\s*(?:по [\w\s]+)?([\d]{2}\.[\d]{2}\.[\d]{4} [\d]{2}:[\d]{2}(?::[\d]{2})?)',
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
            except ValueError:
                return None