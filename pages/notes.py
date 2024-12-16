import streamlit as st
import pypdfium2 as pdfium
import logging, os, time
from io import BytesIO
from utils.obsidian import get_vault_path, create_obsidian_note
from utils.preprocess import preprocess_file
from utils.directory_manager import get_folder_structure
from utils.cypher.key import get_api_key
from utils.llm import get_providers, get_models, generate_notes, format_notes, MissingAPIKeyError

log_file_path = "runtime_log.log"
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

st.set_page_config(layout="centered")

VAULT, _ = get_vault_path()
vault_name = VAULT.split("\\")[-1] + '/'
if VAULT and (not VAULT.endswith("\\")):
    VAULT += "\\"

if 'disabled' not in st.session_state:
    st.session_state.disabled = False
if "folder_name" not in st.session_state:
    st.session_state.folder_name = None
if "use_same" not in st.session_state:
    st.session_state.use_same = True
if "ocr_enhance" not in st.session_state:
    st.session_state.ocr_enhance = False
if "model_generation" not in st.session_state:
    st.session_state.model_generation = 0
if "model_formatting" not in st.session_state:
    st.session_state.model_formatting = 0

def disable_widgets():
    st.session_state.disabled = True
def enable_widgets():
    st.session_state.disabled = False

logger.info("Starting Streamlit application.")

with st.sidebar:
    try:
        folder_structure = get_folder_structure(VAULT)
        logger.info("Retrieved folder structure: %s", folder_structure)

        if folder_structure:
            selected_folder = st.selectbox(
                    vault_name,
                    folder_structure,
                    index=None,
                    placeholder="Root",
                    disabled=st.session_state.disabled
                )
        else:
            if not st.session_state.folder_name:
                selected_folder = st.text_input(vault_name, placeholder='Enter folder name', help='Create a new folder inside vault.', disabled=st.session_state.disabled)
                st.session_state.folder_name = selected_folder
            else:
                selected_folder = st.text_input("Enter Folder Name", value=st.session_state.folder_name, disabled=st.session_state.disabled)
        
        obsidian_db = VAULT
        if selected_folder == '' or selected_folder == None:
            selected_folder = "root"
        print("Selected Folder:", selected_folder)
        if selected_folder != "root":
            obsidian_db = VAULT + selected_folder + '\\'
        logger.info("Selected folder: %s", selected_folder)

        providers = get_providers()
        generation_models, formatting_models = get_models(providers)
        model_generation = st.selectbox('Notes Generation model:', generation_models, index=st.session_state.model_generation, disabled=st.session_state.disabled)
        st.session_state.model_generation = generation_models.index(model_generation)
        model_formatting = None

        st.session_state.use_same = st.checkbox('Use same model for formatting', value=st.session_state.use_same, disabled=st.session_state.disabled)
        if not st.session_state.use_same:
            model_formatting = st.selectbox('Notes Formatting model:', formatting_models, index=st.session_state.model_formatting, disabled=st.session_state.disabled)
            st.session_state.model_formatting = formatting_models.index(model_formatting)
        else:
            model_formatting = model_generation
        logger.info("Selected models - Generation: %s, Formatting: %s", model_generation, model_formatting)
        
        st.session_state.ocr_enhance = st.toggle('Use OCR Enhance', value=st.session_state.ocr_enhance, disabled=st.session_state.disabled)
        ocr_enhance = st.session_state.ocr_enhance
        logger.info("OCR Enhance enabled: %s", ocr_enhance)

    except Exception as e:
        logger.error("Error in sidebar setup: %s", e)


st.write('### ***Turn your Pictures/PDFs into notes***')
title = st.text_input('Note Title', value='New Note', disabled=st.session_state.disabled)
if title == "":
    title = "New Note"

uploaded_files = st.file_uploader(
    'Upload Pictures or PDFs', 
    type=['pdf', 'png', 'jpg'], 
    accept_multiple_files=True, 
    help="Only png, jpg, jpeg and pdf files are supported", 
    disabled=st.session_state.disabled
    )

file_content = None
image_path = None
ocr_result = None
notes = None
formatted_notes = None
note_path = None

if uploaded_files and obsidian_db:
    logger.info("Number of uploaded files: %d", len(uploaded_files))

    all_done = 0
    take_notes_button = st.button(
                                'Take Notes', 
                                use_container_width=True, 
                                # on_click=disable_widgets
                                )
    progress_bar = st.progress(0)

    if take_notes_button:
        for i, file in enumerate(uploaded_files):
            with st.status('Reading file...', expanded=False) as status:
                try:
                    file_content, image_path, ocr_result = preprocess_file(file, ocr_enhance)
                    logger.info("File preprocessed successfully: %s", file.name)
                    progress_bar.progress((4 * i + 1) / (4 * len(uploaded_files)))
                except Exception as e:
                    logger.error("Error processing file: %s; %s", file.name, e, exc_info=True)
                    st.warning(f"An error occurred while processing file: {file.name}")

                if file_content or image_path or ocr_result:
                    try:
                        st.write('Generating Notes...')
                        status.update(label='Generating Notes...')
                        notes = generate_notes(file=file_content, image_path=image_path, ocr_enhance_info=ocr_result, model=model_generation)
                        logger.info("Notes generated successfully for file: %s", file.name)
                        progress_bar.progress((4 * i + 2) / (4 * len(uploaded_files)))
                    except MissingAPIKeyError as e:
                        logger.error(f"{e}")
                        st.error(f"{e}")
                    except Exception as e:
                        logger.error("Error generating notes for file %s: %s", file.name, e, exc_info=True)
                        st.info(f"An error occurred while generating notes for {file.name}")

                if image_path:
                    os.remove(image_path)
                    logger.info("Temporary image file removed: %s", image_path)

                if notes:
                    try:
                        st.write('Formatting Notes...')
                        status.update(label='Formatting Notes...')
                        formatted_notes = format_notes(notes=notes, model=model_formatting)
                        logger.info("Notes formatted successfully for file: %s", file.name)
                        progress_bar.progress((4 * i + 3) / (4 * len(uploaded_files)))
                    except MissingAPIKeyError as e:
                        logger.error(f"{e}")
                        st.info(f"{e}")
                    except Exception as e:
                        logger.error("Error formatting notes for file %s: %s", file.name, e, exc_info=True)
                        st.info(f"An error occurred while formatting notes for {file.name}")

                if formatted_notes:
                    try:
                        st.write('Writing to file...')
                        status.update(label='Writing to file...')
                        note_path = create_obsidian_note(
                            note_title=title,
                            note_content=formatted_notes,
                            vault_path=obsidian_db,
                            uploaded_file=file
                        )
                        progress_bar.progress((4 * i + 4) / (4 * len(uploaded_files)))
                    except Exception as e:
                        logger.error("Error creating notes for file %s: %s", file.name, e, exc_info=True)
                        st.info(f"An error occurred while creating notes file for {file.name}")

                if note_path:
                    all_done += 1
                    st.write(f"Notes created successfully!")
                    logger.info("Notes created successfully: %s", note_path)
                    status.update(label='Notes Created Successfully!', state='complete', expanded=False)
                    
                else:
                    status.update(label='Notes Creation Failed!', state='error', expanded=True)
                    st.error(f"Notes creation failed!")
                    logger.error("Notes creation failed for file: %s", file.name, exc_info=True)
                    break
                
        enable_widgets()
        if all_done == len(uploaded_files) and all_done > 0:
            st.snow()
            st.balloons()
