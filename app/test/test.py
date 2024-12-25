import os
from PyPDF2 import PdfReader
import re

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
                date_time = match.group(1)
                return True, date_time
            else:
                return False, "Дата и время не найдены"
    except Exception as e:
        return False, f"Ошибка при обработке файла {e}"

def extract_texts_from_pdfs_in_folder(folder_path):
    pdf_texts = {}
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            file_path = os.path.join(folder_path, filename)
            success, text = extract_text_from_pdf(file_path)
            if success:
                pdf_texts[filename] = text
            else:
                print(text)  # Вывод ошибки
    return pdf_texts

# Пример использования
folder_path = 'C://Users//zhans//Documents//code//payment bot//app//test//pdfiles'
pdf_texts = extract_texts_from_pdfs_in_folder(folder_path)
for filename, text in pdf_texts.items():
    print(f"Дата и время из файла {filename}:\n{text}\n")