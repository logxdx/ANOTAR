import streamlit as st
import os
from utils.cypher.key import load_or_generate_key
from dotenv import load_dotenv, set_key, unset_key

# Load environment variables
ENV_FILE = ".env"
load_dotenv(ENV_FILE, override=True)


# Function to save API keys to .env
def save_api_key_to_env(provider, key_name, encrypted_key):
    set_key(ENV_FILE, key_name, encrypted_key)


# Function to load API keys from .env
def load_api_keys_from_env(providers):
    api_keys = {}
    for key_name in providers:
        key = os.getenv(key_name)
        if key:
            api_keys[key_name] = key
    return api_keys


# Streamlit app
st.title("Settings Page")

# API keys and their corresponding provider names
all_keys = {
    "GEMINI_API_KEY": "Gemini API key",
    "OPENAI_API_KEY": "OpenAI API Key",
    "OPENAI_ENDPOINT": "OpenAI Endpoint",
    "GROQ_API_KEY": "Groq API key",
    "GDRIVE_FOLDER_ID": "Google Drive Folder ID",
    "OBSIDIAN_VAULT_PATH": "Obsidian Vault Path",
}

# Initialize encryption
cipher = load_or_generate_key()

# Load existing API keys from .env
loaded_keys = load_api_keys_from_env(all_keys.keys())
loaded_providers = [all_keys[key] for key in loaded_keys]
available_keys = {key: provider for key, provider in all_keys.items() if provider not in loaded_providers}

# Initialize session state for selected providers and API keys
if "selected_providers" not in st.session_state:
    st.session_state.selected_providers = {provider: False for provider in all_keys.values()}

if "confirm_deletion" not in st.session_state:
    st.session_state.confirm_deletion = {}

# Display loaded keys
if loaded_providers:
    st.subheader("Loaded Keys")
    for key_name, provider in all_keys.items():
        if provider in loaded_providers:
            st.write(f"**{provider}**")
            
            # Confirmation before deletion
            if not st.session_state.confirm_deletion.get(key_name, False):
                if st.button(f"Remove Key", key=f"{key_name}_remove"):
                    st.session_state.confirm_deletion[key_name] = True
            else:
                st.warning(f"Are you sure you want to remove the {provider} API key?")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Confirm", key=f"{key_name}_confirm"):
                        unset_key(ENV_FILE, key_name)  # Clear key from .env
                        if key_name in os.environ:
                            del os.environ[key_name]
                        st.session_state.confirm_deletion[key_name] = False
                        st.rerun()
                
                with col2:
                    if st.button("Cancel", key=f"{key_name}_cancel"):
                        st.session_state.confirm_deletion[key_name] = False

# Add new keys
if available_keys:
    st.subheader("Add Keys")
    for key_name, provider in available_keys.items():
        # Checkbox to select the provider
        st.session_state.selected_providers[provider] = st.checkbox(
            f"{provider}",
            value=st.session_state.selected_providers.get(provider, False),
            key=f"{provider}_checkbox"
        )
        
        if st.session_state.selected_providers[provider]:
            # For OpenAI, allow both endpoint and API key entry
            if provider == "OpenAI Endpoint" or provider == "OpenAI API Key":
                endpoint = st.text_input(
                    "Enter OpenAI API Endpoint",
                    key="OPENAI_ENDPOINT_input",
                )
                api_key = st.text_input(
                    "Enter OpenAI API Key",
                    type="password",
                    key="OPENAI_API_KEY_input",
                )

                if st.button("Save OpenAI Details", key=f"{provider}_save"):
                    if endpoint:
                        encrypted_endpoint = cipher.encrypt(endpoint.encode("utf-8")).decode("utf-8")
                        save_api_key_to_env("OpenAI", "OPENAI_ENDPOINT", encrypted_endpoint)
                    if api_key:
                        encrypted_api_key = cipher.encrypt(api_key.encode("utf-8")).decode("utf-8")
                        save_api_key_to_env("OpenAI", "OPENAI_API_KEY", encrypted_api_key)

                    st.session_state.selected_providers["OpenAI Endpoint"] = False
                    st.session_state.selected_providers["OpenAI API Key"] = False
                    st.rerun()

            else:
                # Generic key input field
                api_key = st.text_input(
                    f"Enter API Key for {provider}",
                    type="password",
                    key=f"{key_name}_input"
                )

                # Save button for the selected provider
                if st.button(f"Save API Key", key=f"{key_name}_save"):
                    if api_key:  # Only save non-empty keys
                        encrypted_key = cipher.encrypt(api_key.encode("utf-8")).decode("utf-8")
                        save_api_key_to_env(provider, key_name, encrypted_key)
                        
                        # Reset the checkbox and key input
                        st.session_state.selected_providers[provider] = False
                        st.rerun()
