import os
from PyPDF2 import PdfReader
import re
from datetime import datetime

def extract_text_from_pdf(file_path):
    try:
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            # Improved regex pattern to capture date and time with optional text in between
            match = re.search(r'Дата и время\s*(?:по [\w\s]+)?([\d]{2}\.[\d]{2}\.[\d]{4} [\d]{2}:[\d]{2}(?::[\d]{2})?)', text)
            if match:
                date_time_str = match.group(1)
                # Try parsing with seconds first, then without seconds
                try:
                    date_time = datetime.strptime(date_time_str, '%d.%m.%Y %H:%M:%S')
                except ValueError:
                    date_time = datetime.strptime(date_time_str, '%d.%m.%Y %H:%M')
                current_month = datetime.now().month
                if date_time.month == current_month:
                    return True, date_time_str
                else:
                    return True, f"{date_time_str} (Дата не в текущем месяце)"
            else:
                return False, "Дата и время не найдены"
    except Exception as e:
        return False, f"Ошибка при обработке файла {e}"

def extract_texts_from_pdfs_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            file_path = os.path.join(folder_path, filename)
            success, text = extract_text_from_pdf(file_path)
            if success:
                print(f"{filename}: {text}")
            else:
                print(f"{filename}: {text}")

# Пример использования
folder_path = 'C://Users//zhans//Documents//code//payment bot//app//test//pdfiles'
extract_texts_from_pdfs_in_folder(folder_path)