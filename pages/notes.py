import streamlit as st
import pypdfium2 as pdfium
import logging, os, time
from io import BytesIO
from utils.obsidian import get_vault_path, create_obsidian_note
from utils.preprocess import preprocess_file
from utils.directory_manager import get_folder_structure
from utils.cypher.key import get_api_key
from utils.llm import GENERATION_MODELS, FORMATTING_MODELS, MODEL_PROVIDER_MAPPING, generate_notes, format_notes, MissingAPIKeyError

log_file_path = "runtime_log.log"
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

st.set_page_config(layout="centered")

VAULT, _ = get_vault_path()
vault_name = VAULT.split("\\")[-1] + '/'
if VAULT and (not VAULT.endswith("\\")):
    VAULT += "\\"

if "folder_name" not in st.session_state:
    st.session_state.folder_name = None

logger.info("Starting Streamlit application.")

with st.sidebar:
    try:
        folder_structure = get_folder_structure(VAULT)
        logger.info("Retrieved folder structure: %s", folder_structure)

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
                    st.session_state.folder_name = selected_folder
                else:
                    selected_folder = st.session_state.folder_name
        else:
            if not st.session_state.folder_name:
                selected_folder = st.text_input(vault_name, placeholder='Enter folder name', help='Create a new folder inside vault.')
                st.session_state.folder_name = selected_folder
            else:
                selected_folder = st.text_input("Enter Folder Name", value=st.session_state.folder_name)
        
        obsidian_db = VAULT
        if selected_folder != 'Root' and selected_folder != 'New Folder' and selected_folder != '':
            obsidian_db = VAULT + selected_folder + '\\'
        logger.info("Selected folder: %s", selected_folder)

        model = st.selectbox('Model for Notes Generation', GENERATION_MODELS)
        model_formatting = st.selectbox('Model for Notes Formatting', FORMATTING_MODELS)
        logger.info("Selected models - Generation: %s, Formatting: %s", model, model_formatting)

        ocr_enhance = st.toggle('Use OCR Enhance', False)
        logger.info("OCR Enhance enabled: %s", ocr_enhance)

    except Exception as e:
        logger.error("Error in sidebar setup: %s", e, exc_info=True)

st.write('### ***Turn your Pictures/PDFs into notes***')
title = st.text_input('Note Title', value='New Note')
if title == "":
    title = "New Note"

uploaded_files = st.file_uploader('Upload Pictures or PDFs', type=['pdf', 'png', 'jpg'], accept_multiple_files=True, help="Only png, jpg, jpeg and pdf files are supported")

file_content = None
image_path = None
ocr_result = None
notes = None
formatted_notes = None
note_path = None

if uploaded_files and obsidian_db:
    logger.info("Number of uploaded files: %d", len(uploaded_files))

    all_done = 0
    take_notes_button = st.button('Take Notes', use_container_width=True)
    progress_bar = st.progress(0)

    if take_notes_button:
        for i, file in enumerate(uploaded_files):
            with st.status('Working on file...', expanded=False) as status:
                try:
                    st.write(f'Processing file: {file.name}')
                    file_content, image_path, ocr_result = preprocess_file(file, ocr_enhance)
                    logger.info("File preprocessed successfully: %s", file.name)
                    progress_bar.progress((4 * i + 1) / (4 * len(uploaded_files)))
                except Exception as e:
                    logger.error("Error processing file %s: %s", file.name, e, exc_info=True)
                    st.error(f"An error occurred while processing {file.name} \nCheck runtime logs for more details.")

                if file_content or image_path or ocr_result:
                    try:
                        st.write(f'Generating Notes...')
                        notes = generate_notes(file=file_content, image_path=image_path, ocr_enhance_info=ocr_result, model=model)
                        logger.info("Notes generated successfully for file: %s", file.name)
                        progress_bar.progress((4 * i + 2) / (4 * len(uploaded_files)))
                    except MissingAPIKeyError as e:
                        st.error(f"{e}")
                    except Exception as e:
                        logger.error("Error generating notes for file %s: %s", file.name, e, exc_info=True)
                        st.error(f"An error occurred while generating notes for {file.name} \nCheck runtime logs for more details.")

                if image_path:
                    os.remove(image_path)
                    logger.info("Temporary image file removed: %s", image_path)

                if notes:
                    try:
                        st.write(f'Formatting Notes...')
                        formatted_notes = format_notes(notes=notes, model=model_formatting)
                        logger.info("Notes formatted successfully for file: %s", file.name)
                        progress_bar.progress((4 * i + 3) / (4 * len(uploaded_files)))
                    except MissingAPIKeyError as e:
                        st.error(f"{e}")
                    except Exception as e:
                        logger.error("Error formatting notes for file %s: %s", file.name, e, exc_info=True)
                        st.error(f"An error occurred while formatting notes for {file.name} \nCheck runtime logs for more details.")

                if formatted_notes:
                    try:
                        st.write(f'Creating Notes...')
                        note_path = create_obsidian_note(
                            note_title=title,
                            note_content=formatted_notes,
                            vault_path=obsidian_db,
                            uploaded_file=file
                        )
                        progress_bar.progress((4 * i + 4) / (4 * len(uploaded_files)))
                    except Exception as e:
                        logger.error("Error creating notes for file %s: %s", file.name, e, exc_info=True)
                        st.error(f"An error occurred while creating notes for {file.name} \nCheck runtime logs for more details.")

                if note_path:
                    all_done += 1
                    st.write(f"Notes created successfully!")
                    logger.info("Notes created successfully: %s", note_path)
                    status.update(label='Notes Created Successfully!', state='complete', expanded=False)
                else:
                    st.write(f"Notes creation failed!")
                    status.update(label='Notes Creation Failed!', state='error', expanded=True)
                    logger.warning("Notes creation failed for file: %s", file.name)


        if all_done == len(uploaded_files) and all_done > 0:
            st.balloons()
            st.snow()
