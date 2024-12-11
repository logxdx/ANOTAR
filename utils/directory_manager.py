from dotenv import load_dotenv
from utils.cypher.key import get_api_key, ENV_FILE
import os

load_dotenv(ENV_FILE, override=True)

VAULT = get_api_key("OBSIDIAN_VAULT_PATH")


def get_folder_structure(base_path):
    """
    Recursively get the folder structure starting from base_path
    
    Args:
        base_path (str): Root directory to start exploring
    
    Returns:
        list: List of relative paths to folders
    """

    if not base_path:
        return

    folder_paths = []
    
    # Ensure the base path exists
    if not os.path.exists(base_path):
        return folder_paths
    
    # Walk through the directory
    for root, dirs, _ in os.walk(base_path):
        # Filter out hidden directories in-place
        dirs[:] = [dir for dir in dirs if not dir.startswith('.') and dir != 'assets']
        
        for dir in dirs:
            # Create relative path
            full_path = os.path.join(root, dir)
            relative_path = os.path.relpath(full_path, base_path)
            
            # Add to folder paths
            folder_paths.append(relative_path)
    
    return sorted(folder_paths)

def list_directory_tree(path, indent=0, base_url=None):
    tree = ""
    try:
        for entry in os.scandir(path):
            if entry.name.startswith(".") or entry.name == "assets" or entry.name.endswith(".ini"):
                continue
            
            prefix = "├─" + "──" * indent
            
            if entry.is_dir():
                if indent == 0:
                    tree += "---\n"
                tree += f"{prefix}📂 ***{entry.name}***\n\n"
                tree += list_directory_tree(entry.path, indent + 1, base_url)
            else:
                if base_url:
                    relative_path = os.path.relpath(entry.path, start=VAULT).replace(" ", "%20")
                    file_url = f"{base_url}&file={relative_path}"
                    tree += f"{prefix}📄 [{entry.name}]({file_url})\n\n"
                else:
                    tree += f"{prefix}📄 {entry.name}\n\n"
    except PermissionError:
        tree += f"{' ' * (4 * indent)}❌ Permission Denied: {path}\n"
    return tree

