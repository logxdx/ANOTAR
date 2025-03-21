import easyocr, re, os
import pypdfium2 as pdfium
from PIL import Image

def ocr(image_path: str):
    try:
        reader = easyocr.Reader(['ch_sim','en'])
        result = reader.readtext(image_path, detail=0)
        return " ".join(result)
    except Exception as e:
        print("Error during OCR:", e)

def preprocess_pdf(pdf, ocr_enhance=False):
    text = ""
    ocr_result = ""
    pages = pdfium.PdfDocument(pdf)
    for page in pages:
        t = page.get_textpage().get_text_range()
        if t:
            text += t

    text = text.strip()
    alpha_chars = len(re.findall(r'[a-zA-Z]', text))
    if len(text) == 0 or alpha_chars / len(text) < 0.3:
        ocr_enhance = True

    if ocr_enhance:
        for i in range(len(pages)):
            name = f"./ocr/page{i}.png"
            page = pages[i]
            image = page.render(scale=4).to_pil()
            image.save(f'{name}')
            ocr_result += str(ocr(f'{name}')) + '\n'
            os.remove(f'{name}')

    return text, None, ocr_result

def preprocess_image(image):
    ocr_result = ""
    name = "./ocr/ocr.png"
    image = Image.open(image)
    image.save(f'{name}')
    image_path = f"{name}"
    ocr_result += str(ocr(image_path))

    return None, image_path, ocr_result

def preprocess_file(file, ocr_enhance=False):
    print("Processing file...")
    if file.name.lower().endswith('.pdf'):
        print("pdf file detected.")
        results = preprocess_pdf(file, ocr_enhance)
    else:
        results = preprocess_image(file)

    if results:
        print("Preprocessing completed.")
        return results
    else:
        print("Error during preprocessing.")
        return None, None, None
        
