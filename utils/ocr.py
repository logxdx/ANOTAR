import easyocr
import pypdfium2 as pdfium

def ocr(image_path: str):
    try:
        reader = easyocr.Reader(['ch_sim','en'])
        result = reader.readtext(image_path, detail=0)
        return " ".join(result)
    except Exception as e:
        print("Error during OCR:", e)

def extract_text_from_pdf(pdf):
    try:
        text = ""
        pages = pdfium.PdfDocument(pdf)
        for page in pages:
            t = page.get_textpage().get_text_range()
            if t:
                text += t
        return text
    except Exception as e:
        print("Error during PDF text extraction:", e)