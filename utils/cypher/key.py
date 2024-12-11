import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv, set_key, unset_key

KEY_FILE = "secret.key"
ENV_FILE = ".env"

# Load environment variables
load_dotenv(ENV_FILE, override=True)

# API keys and their corresponding provider names
ALL_KEYS = {
    "Google Gemini":["GEMINI_API_KEY"],
    "OpenAI": ["OPENAI_API_KEY", "OPENAI_ENDPOINT"],
}

# Function to encrypt a key
def encrypt_key(key: str) -> str:
    print("Key:", key)
    encryption_key = load_or_generate_key()
    key = key.encode('utf-8')
    encrypted_api_key = encryption_key.encrypt(key)
    return encrypted_api_key.decode('utf-8')

# Function to load API keys from .env
def load_api_keys_from_env(providers):
    api_keys = {}
    for provider, keys in providers:
        for key_name in keys:
            key = os.getenv(key_name)
            if key:
                key  = key.encode('utf-8')
                api_keys[key_name] = key
    return api_keys

# Function to save API keys to .env
def save_api_key_to_env(key_name, key):
    encrypted_key = encrypt_key(key)
    set_key(ENV_FILE, key_name, encrypted_key)
    print("Saved key for", key_name)

# Function to remove API keys from .env
def remove_api_key_from_env(key_name):
    unset_key(ENV_FILE, key_name)
    if key_name in os.environ:
        del os.environ[key_name]
    print("Deleted key for", key_name)

# Function to load or generate an encryption key
def load_or_generate_key():
    # Check if the key already exists in the environment
    try:
        with open(KEY_FILE, 'rb') as key_file:
            key = key_file.read()
    except FileNotFoundError:
        key = None

    if not key:
        # Generate a new key if it doesn't exist
        key = Fernet.generate_key()
        
        # Save the key to the .env file
        with open(KEY_FILE, 'wb') as key_file:
            key_file.write(key)
    
    return Fernet(key)

# Function to decrypt a key
def get_api_key(key_name: str) -> str:
    encryption_key = load_or_generate_key()
    key = os.getenv(key_name)
    decrypted_key = None
    if key:    
        decrypted_key = encryption_key.decrypt(key)
        decrypted_key = decrypted_key.decode("utf-8")
    return decrypted_key

