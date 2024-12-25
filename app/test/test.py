import os
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import pytesseract

def extract_text_from_pdf(file_path):
    try:
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            text = ""
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += page_text
                else:
                    # Если текст не найден, используем OCR
                    images = convert_from_path(file_path, first_page=page_num + 1, last_page=page_num + 1)
                    for image in images:
                        text += pytesseract.image_to_string(image)
            return True, text
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
    print(f"Текст из файла {filename}:\n{text}\n")