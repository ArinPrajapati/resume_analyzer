import pdfplumber
from typing import BinaryIO


def extract_text_from_pdf(pdf_file: BinaryIO) -> str:
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            print(page)
            text += page.extract_text() or ""

    return text.strip()
