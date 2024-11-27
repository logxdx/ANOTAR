import easyocr
import pypdfium2 as pdfium

def ocr(image_path: str):
    reader = easyocr.Reader(['ch_sim','en'])
    result = reader.readtext(image_path, detail=0)
    return result

def extract_text_from_pdf(pdf):
    text = ""

    pages = pdfium.PdfDocument(pdf)
    for page in pages:
        t = page.get_textpage().get_text_range()
        if t:
            text += t

    return text