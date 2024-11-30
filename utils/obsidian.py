import os

def create_obsidian_note(note_title: str, note_content:str, vault_path: str, uploaded_file):
    """
    Adds uploaded file and note content to an Obsidian note. Creates a new note if it doesn't exist.
    
    :param note_title: Title of the Obsidian note.
    :param vault_path: Path to the Obsidian vault.
    :param uploaded_file: File-like object of the uploaded image.
    """

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
    
    with open(note_path, 'a') as note_file:
        note_file.write('\n' + image_markdown + '\n')
        note_file.write(note_content)
        note_file.write('\n---\n')
    
    return note_path
