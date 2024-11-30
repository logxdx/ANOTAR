import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()
ENV_FILE = ".env"
ENV_KEY_NAME = "SHADOW_SWORD"

def load_or_generate_key():
    # Check if the key already exists in the environment
    encryption_key = os.getenv(ENV_KEY_NAME)

    if not encryption_key:
        # Generate a new key if it doesn't exist
        key = Fernet.generate_key()
        encryption_key = key.decode('utf-8')
        
        # Save the key to the .env file
        with open(ENV_FILE, 'a') as env_file:
            env_file.write(f"{ENV_KEY_NAME} = {encryption_key}\n")

    return Fernet(encryption_key)

def get_api_key(key_name: str) -> str:
    return load_or_generate_key().decrypt(os.getenv(key_name).encode('utf-8')).decode('utf-8')
