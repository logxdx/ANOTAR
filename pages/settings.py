import streamlit as st
import os, json
from utils.cypher.key import load_or_generate_key, load_api_keys_from_env, save_api_key_to_env, remove_api_key_from_env, encrypt_key
from utils.obsidian import get_vault_path
from dotenv import load_dotenv

config = json.load(open("config.json"))
PROVIDER_KEYS = config["PROVIDER_KEYS"]
ENV_FILE = config["ENV_FILE"]

load_dotenv(ENV_FILE, override=True)

st.subheader("Vault Path")
obsidian_db, _ = get_vault_path()
if _:
    st.info("Using default vault path")

edit_path = st.button("Edit vault path", type="primary")
if not st.session_state.get("edit_path", False):
    st.session_state.edit_path = edit_path
if st.session_state.edit_path:
    new_path = st.text_input("Enter Vault Path", value=obsidian_db, key="vault_path_input", help="Clear to set default path")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Save", type="primary"):
            save_api_key_to_env("OBSIDIAN_VAULT_PATH", new_path)
            st.session_state.edit_path = False
            st.rerun()
    with col2:
        if st.button("Cancel"):
            st.session_state.edit_path = False
            st.rerun()

st.write("---")

# Load existing API keys from .env
loaded_keys = load_api_keys_from_env(PROVIDER_KEYS.items())
available_providers = {provider: keys for provider, keys in PROVIDER_KEYS.items() if any(key not in loaded_keys for key in keys)}

# Initialize session state for selected providers and API keys
if "selected_providers" not in st.session_state:
    st.session_state.selected_providers = {provider: False for provider in PROVIDER_KEYS.keys()}

if "confirm_deletion" not in st.session_state:
    st.session_state.confirm_deletion = {}

# Display loaded keys
if loaded_keys:
    st.subheader("Available Providers")
    for provider, keys in PROVIDER_KEYS.items():
        if provider not in available_providers.keys():
            st.write(f"**{provider}**")
            if not st.session_state.confirm_deletion.get(provider, False):
                if st.button(f"Remove Key", key=f"{provider}_remove"):
                    st.session_state.confirm_deletion[provider] = True
            else:
                st.error(f"Are you sure you want to remove {provider}?")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Confirm", key=f"{provider}_confirm", type="primary"):
                        for key_name in keys:
                            remove_api_key_from_env(key_name)
                        st.session_state.confirm_deletion[provider] = False
                        st.rerun()
                
                with col2:
                    if st.button("Cancel", key=f"{provider}_cancel"):
                        st.session_state.confirm_deletion[provider] = False

st.write("---")

# Add new keys
if available_providers:
    st.subheader("More Providers")
    for provider, keys in available_providers.items():
        st.session_state.selected_providers[provider] = st.checkbox(
            f"{provider}",
            value=st.session_state.selected_providers.get(provider, False),
            key=f"{provider}_checkbox"
        )
        if st.session_state.selected_providers[provider]:
            if provider == 'Ollama':
                for key in keys:
                    save_api_key_to_env(key, "Ollama")
                    st.session_state.selected_providers[provider] = False
                    st.rerun()
            else:            
                for key_name in keys:
                    api_key = st.text_input(
                        f"{key_name}",
                        type="password",
                        key=f"{key_name}_input"
                    )
                    if st.button(f"Save", key=f"{key_name}_save", type="primary"):
                        if api_key:
                            save_api_key_to_env(key_name, api_key)                        
                            st.session_state.selected_providers[provider] = False
                            st.rerun()