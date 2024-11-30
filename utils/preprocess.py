import easyocr
import pypdfium2 as pdfium

def ocr(image_path: str):
    try:
        reader = easyocr.Reader(['ch_sim','en'])
        result = reader.readtext(image_path, detail=0)
        return " ".join(result)
    except Exception as e:
        print("Error during OCR:", e)

def preprocess_pdf(pdf, ocr_enhance=False):
    try:
        text = ""
        ocr_result = ""
        pages = pdfium.PdfDocument(pdf)
        for page in pages:
            t = page.get_textpage().get_text_range()
            if t:
                text += t

        alpha_chars = len(re.findall(r'[a-zA-Z]', text))
        if alpha_chars / len(text) < 0.3:
            ocr_enhance = True

        if ocr_enhance:
            for i in range(len(pages)):
                name = f".\ocr\page{i}.png"
                page = pages[i]
                image = page.render(scale=4).to_pil()
                image.save(f'{name}')
                ocr_result += ocr(f'{name}') + '\n'
                os.remove(f'{name}')

        return text, None, ocr_result

    except Exception as e:
        print("Error during PDF text extraction:", e)

def preprocess_image(image):
    ocr_result = ""
    try:
        name = ".\ocr\ocr.png"
        image = Image.open(file)
        image.save(f'{name}')
        image_path = f"{name}"
        ocr_result += ocr(image_path)

        return None, image_path, ocr_result

    except Exception as e:
        print("Error during image OCR:", e)

def preprocess_file(file, ocr_enhance=False):
    if file.name.lower().endswith('.pdf'):
        return preprocess_pdf(file, ocr_enhance)
    else:
        return preprocess_image(file)
        
