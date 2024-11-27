import streamlit as st
from dotenv import load_dotenv
import pypdfium2 as pdfium
import logging, os
from PIL import Image
from io import BytesIO
from utils.notion import *
from utils.obsidian import *
from utils.ocr import *
from utils.llm import *

load_dotenv()

log_file_path = "runtime_log.log"
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

default_vault_path = os.getenv("OBSIDIAN_VAULT_PATH")

with st.sidebar:
    import qrcode, os
    from io import BytesIO
    from streamlit.web.server import server_util
    internal_ip = st.net_util.get_internal_ip()
    url = server_util.get_url(internal_ip)
    img = qrcode.make(url)

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_bytes = buffer.getvalue()

    st.image(img_bytes, caption=f"scan to open: {url}", use_container_width=True)
    obsidian_db = st.text_input('Obsidian Directory', value=default_vault_path)
    model = st.selectbox('Model for Notes Generation', ['gemini-1.5-flash', 'gemini-1.5-flash-8b', 'gpt-4o-mini', 'gpt-4o', 'ollama-minicpm-v', 'ollama-llama3.2-vision'])
    model_formatting = st.selectbox('Model for Notes Formatting', ['gemini-1.5-flash', 'gemini-1.5-flash-8b', 'gpt-4o-mini', 'gpt-4o', 'ollama-qwen2', 'ollama-qwen2.5', 'ollama-llama3.2'])

    ocr_enhance = st.toggle('Use OCR Enhance', False)

st.title('Turn your photos and PDFs into notes with AI')
title = st.text_input('Note Title', value='New Note')
if title == "":
    title = "New Note"
uploaded_files = st.file_uploader('Upload photos or PDFs', accept_multiple_files=True)

take_notes_button = st.button('Take Notes', use_container_width=True)

if take_notes_button:
    all_done = 0
    if uploaded_files is not None:
        for file in uploaded_files:
            print()
            image_path = None
            pdf = None
            file_type = None
            status_code = 200

            if file.name.lower().endswith('.pdf'):
                logging.info(f"Processing PDF file.")
                pdf = extract_text_from_pdf(file)
                file_type = "pdf"
            else:
                logging.info(f"Processing image file.")
                image = Image.open(file)
                image.save(f'./ocr/{file.name}')
                image_path = f"./ocr/{file.name}"
                file_type = "image"

            with st.spinner('Taking notes...'):
                note_path = prepare_obsidian_writepath(note_title=title, vault_path=obsidian_db, uploaded_file=file)
                ocr_result = []

                if ocr_enhance:
                    name = "ocr.png"
                    if file_type == "pdf":
                        pages = pdfium.PdfDocument(file)
                        for i in range(len(pages)):
                            page = pages[i]
                            image = page.render(scale=4).to_pil()
                            image.save(f'./ocr/{name}')
                            ocr_result += ocr(f'./ocr/{name}')
                        os.remove(f'./ocr/{name}')
                    else:
                        image.save(f'./ocr/{name}')
                        ocr_result = ocr(f'./ocr/{name}')
                        os.remove(f'./ocr/{name}')
                    logging.info(f"OCR results generated")

                notes_gen = generated_notes_from_images(file=pdf, image_path=image_path, ocr_enhance_info=ocr_result, model=model)
                notes_gen = format_notes(notes=notes_gen, model=model_formatting)
                logging.info(f"Notes generated")
                for notes in notes_gen:
                    append_to_obsidian_file(content=notes, file_path=note_path)
                    # status_code = create_notion_page(title=title, content=notes)
                    if status_code != 200:
                        logging.error(f"Failed to create Notion page. Status code: {status_code}")
                        st.write(f"Failed to create Notion page. Status code: {status_code}")
            print("Done\n")
            all_done += 1
            st.success(f'File {all_done} done!')
            logging.info(f"File processing complete.")

        if all_done == len(uploaded_files) and all_done > 0:
            st.balloons()
            logging.info("All files processed successfully.")

