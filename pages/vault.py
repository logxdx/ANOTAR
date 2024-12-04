import streamlit as st
import os
from utils.directory_manager import list_directory_tree
from utils.cypher.key import get_api_key

obsidian_db = get_api_key("OBSIDIAN_VAULT_PATH")
vault_name = obsidian_db.split("\\")[-2]
st.title(f"Obsidian: {vault_name}")

obsidian_base_url = f"obsidian://open?vault={vault_name}"

if os.path.exists(obsidian_db):    
    try:
        st.info("Click on file names to open in Obsidian. Ensure Obsidian is installed and configured.")
        tree_md = list_directory_tree(obsidian_db, base_url=obsidian_base_url)        
        st.write(f"{tree_md}")        
    except Exception as e:
        st.error(f"Error generating directory tree: {str(e)}")
else:
    st.error(f"Obsidian Vault does not exist: {directory}")
