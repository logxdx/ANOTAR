import streamlit as st
from dotenv import load_dotenv
import pypdfium2 as pdfium
import logging, os
from PIL import Image
from io import BytesIO
from utils.obsidian import create_obsidian_note
from utils.preprocess import preprocess_file
from utils.directory_manager import get_folder_structure
from utils.cypher.key import get_api_key
from utils.llm import GENERATION_MODELS, FORMATTING_MODELS, generate_notes, format_notes

load_dotenv()

log_file_path = "runtime_log.log"
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

VAULT = get_api_key("OBSIDIAN_VAULT_PATH")

st.set_page_config(
    page_title="AI Notes",
    page_icon="📝",
)


if "folder_name" not in st.session_state:
    st.session_state.folder_name = None

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
    
    folder_structure = get_folder_structure(VAULT)
    if folder_structure:
        selected_folder = st.selectbox(
                'File Path',
                ['Root', 'New Folder'] + folder_structure,
                index=0,
                placeholder="Select a folder from your vault"
            )

        if selected_folder == "New Folder":
            if not st.session_state.folder_name:
                selected_folder = st.text_input("Enter Folder Name")
            else:
                selected_folder = st.session_state.folder_name
    
    obsidian_db = VAULT
    if selected_folder != 'Root' and selected_folder != 'New Folder':
        obsidian_db = VAULT + selected_folder + '\\'

    model = st.selectbox('Model for Notes Generation', GENERATION_MODELS)
    model_formatting = st.selectbox('Model for Notes Formatting', FORMATTING_MODELS)

    ocr_enhance = st.toggle('Use OCR Enhance', False)

st.title('Turn your Pictures and PDFs into notes')
title = st.text_input('Note Title', value='New Note')
if title == "":
    title = "New Note"

uploaded_files = st.file_uploader('Upload Photos or PDFs', accept_multiple_files=True)
take_notes_button = st.button('Take Notes', use_container_width=True)

if take_notes_button:
    all_done = 0
    if uploaded_files is not None:
        with st.spinner('Taking notes...'):
            for file in uploaded_files:
                file, image_path, ocr_result = preprocess_file(file, ocr_enhance)

                notes = generate_notes(file=file, image_path=image_path, ocr_enhance_info=ocr_result, model=model)
                os.remove(image_path)
                formatted_notes = format_notes(notes=notes, model=model_formatting)

                create_obsidian_note(note_title=title, note_content=formatted_notes, vault_path=obsidian_db, uploaded_file=file)
            
                all_done += 1
                st.success(f'Notes for file {all_done} created!')

        if all_done == len(uploaded_files) and all_done > 0:
            st.balloons()

