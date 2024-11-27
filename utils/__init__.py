import os
import base64

def get_markdown_files_in_path(dir: str):
    files = []
    for file in os.listdir(dir):
        if file.endswith(".md"):
            files.append(file)
    return files