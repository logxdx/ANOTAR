import os
import logging
from utils.cypher.key import get_api_key

logger = logging.getLogger(__name__)

def get_vault_path():
    try:
        logger.info("Attempting to retrieve vault path using API key.")
        vault_path = get_api_key("OBSIDIAN_VAULT_PATH")
        flag = False

        if not vault_path:
            flag = True
            documents_dir = os.path.expanduser("~\\Documents")
            vault_path = os.path.join(documents_dir, "ANOTAR")
            
            if not os.path.exists(vault_path):
                os.makedirs(vault_path, exist_ok=True)
                logger.info("Vault path not found; created default directory: %s", vault_path)
        else:
            vault_path = vault_path.replace('/', '\\')
            if vault_path[-1] == '\\':
                vault_path = vault_path[:-1] 

        logger.info("Vault path determined: %s", vault_path)
        return vault_path, flag
    except Exception as e:
        logger.error("Error while determining vault path: %s", e, exc_info=True)
        raise

def create_obsidian_note(note_title: str, note_content: str, vault_path: str, uploaded_file):
    try:
        logger.info("Starting note creation process for %s", note_title)

        if not os.path.exists(vault_path):
            logger.info("Vault path does not exist. Creating folder: %s", vault_path)
            os.makedirs(vault_path)
        
        note_filename = f"{note_title}.md"
        note_path = os.path.join(vault_path, note_filename)

        note_title = note_title.lower().replace(" ", "_")
        
        filename = uploaded_file.name.lower().replace(" ", "_")

        file_dir = os.path.join(vault_path, f'assets/assets_{note_title}')
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
            logger.info("Image directory created: %s", file_dir)
        
        target_image_path = os.path.join(file_dir, filename)
        
        with open(target_image_path, 'wb') as out_file:
            out_file.write(uploaded_file.getbuffer())
            logger.info("Image saved to: %s", target_image_path)
        
        file_markdown = f"[[{filename}]]\n"
        # note_content = note_content.replace('\\[\n', '$').replace('\n\\]', '$').replace('\\[ ', '$').replace(' \\]', '$').replace('\\[', '$').replace('\\]', '$')
        # note_content = note_content.replace('\\(\n', '$').replace('\n\\)', '$').replace('\\( ', '$').replace(' \\)', '$').replace('\\(', '$').replace('\\)', '$')
        # note_content = note_content.replace("\n```markdown", "\n").replace("\n```", "\n")
        
        with open(note_path, 'a', encoding='utf-8') as note_file:
            note_file.write('\n---\n' + '\n' + file_markdown + '\n' + note_content + '\n' + '\n---\n')
            logger.info("Note content appended to file: %s", note_path)
        
        logger.info("Note created successfully at path: %s", note_path)
        return note_path
    except Exception as e:
        logger.error("Error during note creation: %s", e, exc_info=True)
        raise
