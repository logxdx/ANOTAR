import os
from utils.cypher.key import get_api_key

def get_vault_path():
    """
    Determines the vault path for storing Markdown notes and assets, prioritizing accessibility.
    Defaults to the user's Documents folder across platforms unless overridden by an API key.
    """
    # Try to get the vault path from the API key
    vault_path = get_api_key("OBSIDIAN_VAULT_PATH")
    flag = False
    
    if not vault_path:
        flag = True
        documents_dir = os.path.expanduser("~\\Documents")
        vault_path = os.path.join(documents_dir, "ANOTAR")
        
        if not os.path.exists(vault_path):
            os.makedirs(vault_path)
    else:
        vault_path = vault_path.replace('/', '\\')
        if vault_path[-1] == '\\':
            vault_path = vault_path[:-1] 
    
    return vault_path, flag


def create_obsidian_note(note_title: str, note_content: str, vault_path: str, uploaded_file):
    """
    Adds uploaded file and note content to an Obsidian note. Creates a new note if it doesn't exist.
    
    :param note_title: Title of the Obsidian note.
    :param vault_path: Path to the Obsidian vault.
    :param uploaded_file: File-like object of the uploaded image.
    """

    print(f"Creating Notes...")

    if not os.path.exists(vault_path):
        print(f"'{vault_path}' does not exist. Creating Folder...")
        os.makedirs(vault_path)
    
    note_filename = f"{note_title}.md"
    note_path = os.path.join(vault_path, note_filename)

    note_title = note_title.lower()
    note_title = note_title.replace(" ", "_")
    
    image_filename = uploaded_file.name
    image_filename = image_filename.lower()
    image_filename = image_filename.replace(" ", "_")

    image_dir = os.path.join(vault_path, f'assets/assets_{note_title}')
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    target_image_path = os.path.join(image_dir, image_filename)
    
    with open(target_image_path, 'wb') as out_file:
        out_file.write(uploaded_file.getbuffer())
    
    image_markdown = f"![{image_filename}]({image_filename})\n"
    note_content = note_content.replace('\[\n', '$').replace('\n\]', '$').replace('\\[ ', '$').replace(' \\]', '$').replace('\\[', '$').replace('\\]', '$')
    
    with open(note_path, 'a', encoding='utf-8') as note_file:
        note_file.write('\n---\n' + '\n' + image_markdown + '\n' + note_content + '\n' + '\n---\n')
    
    print(f"Notes created successfully!")
    return note_path
