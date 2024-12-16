import streamlit as st
import os
import time
import shutil
from pathlib import Path
import math
from typing import Optional, List, Dict, Any
from utils.obsidian import get_vault_path

st.set_page_config(layout="wide")

class StreamlitFileManager:
    def __init__(
        self,
        root_path: str = "files",
        key_prefix: str = "",
        items_per_page_options: List[int] = [10, 25, 50, 100]
    ):
        """
        Initialize the File Manager component.
        
        Args:
            root_path (str): Root directory for the file manager
            key_prefix (str): Prefix for session state keys to allow multiple instances
            items_per_page_options (List[int]): Options for items per page in pagination
        """
        self.root_path = root_path
        self.key_prefix = key_prefix
        self.items_per_page_options = items_per_page_options
        self._init_session_state()
        
        # Create root directory if it doesn't exist
        if not os.path.exists(self.root_path):
            os.makedirs(self.root_path)

    def _get_state_key(self, key: str) -> str:
        """Generate a unique session state key."""
        return f"{self.key_prefix}{key}"

    def _init_session_state(self):
        """Initialize session state variables."""
        state_vars = {
            'current_path': self.root_path,
            'previous_path': None,
            'show_new_folder_input': False,
            'show_upload': False,
            'current_page': 1,
            'items_per_page': 10,
            'upload_success': [],
            'upload_progress': 0,
            'page_content' : None,
        }
        
        for key, default_value in state_vars.items():
            state_key = self._get_state_key(key)
            if state_key not in st.session_state:
                st.session_state[state_key] = default_value

    def _get_files_and_folders(self) -> List[Dict[str, Any]]:
        """Get list of files and folders in current directory."""
        items = []
        try:
            for item in os.listdir(st.session_state[self._get_state_key('current_path')]):
                if not item.startswith('.') and not item.endswith('.ini') and not item == 'assets':
                    full_path = os.path.join(
                        st.session_state[self._get_state_key('current_path')], 
                        item
                    )
                    is_directory = os.path.isdir(full_path)
                    items.append({
                        'name': item,
                        'path': full_path,
                        'is_directory': is_directory,
                        'size': os.path.getsize(full_path) if not is_directory else 0,
                        'modified': os.path.getmtime(full_path)
                    })
        except Exception as e:
            print(f"Error accessing path: {e}")
        return items

    def _handle_file_upload(self, uploaded_files) -> bool:
        """Handle file upload process with progress tracking."""
        if not uploaded_files:
            return False
        
        total_files = len(uploaded_files)
        st.session_state[self._get_state_key('upload_success')] = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, uploaded_file in enumerate(uploaded_files, 1):
            try:
                file_path = os.path.join(
                    st.session_state[self._get_state_key('current_path')],
                    uploaded_file.name
                )
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.session_state[self._get_state_key('upload_success')].append(
                    {"name": uploaded_file.name, "status": "success"}
                )
            except Exception as e:
                st.session_state[self._get_state_key('upload_success')].append(
                    {"name": uploaded_file.name, "status": "error", "message": str(e)}
                )
            
            progress = int(idx * 100 / total_files)
            progress_bar.progress(progress)
            status_text.text(f"Uploading file {idx} of {total_files}: {uploaded_file.name}")
        
        success_count = sum(1 for item in st.session_state[self._get_state_key('upload_success')] 
                          if item["status"] == "success")
        st.success(f"Successfully uploaded {success_count} of {total_files} files")
        
        errors = [item for item in st.session_state[self._get_state_key('upload_success')] 
                 if item["status"] == "error"]
        if errors:
            st.error("Failed to upload the following files:")
            for error in errors:
                st.write(f"- {error['name']}: {error['message']}")
        
        return success_count == total_files

    def _create_new_folder(self, folder_name: str) -> bool:
        """Create a new folder in the current directory."""
        try:
            new_folder_path = os.path.join(
                st.session_state[self._get_state_key('current_path')],
                folder_name
            )
            if os.path.exists(new_folder_path):
                st.error("A folder with this name already exists!")
                return False
            os.makedirs(new_folder_path)
            return True
        except Exception as e:
            st.error(f"Error creating folder: {e}")
            return False

    def _delete_item(self, path: str) -> bool:
        """Delete a file or folder."""
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            return True
        except Exception as e:
            st.error(f"Error deleting item: {e}")
            return False

    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def _render_pagination(self, total_items: int):
        """Render pagination controls."""
        total_pages = math.ceil(total_items / st.session_state[self._get_state_key('items_per_page')])
        
        if total_pages > 1:
            col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 2, 1])
            current_page = st.session_state[self._get_state_key('current_page')]
            
            with col1:
                if st.button("⏮️", disabled=current_page == 1, key=f"{self.key_prefix}first"):
                    st.session_state[self._get_state_key('current_page')] = 1
                    st.rerun()
            
            with col2:
                if st.button("◀️", disabled=current_page == 1, key=f"{self.key_prefix}prev"):
                    st.session_state[self._get_state_key('current_page')] -= 1
                    st.rerun()
            
            with col3:
                st.write(f"Page {current_page} of {total_pages}")
            
            with col4:
                if st.button("▶️", disabled=current_page == total_pages, key=f"{self.key_prefix}next"):
                    st.session_state[self._get_state_key('current_page')] += 1
                    st.rerun()
            
            with col5:
                if st.button("⏭️", disabled=current_page == total_pages, key=f"{self.key_prefix}last"):
                    st.session_state[self._get_state_key('current_page')] = total_pages
                    st.rerun()

    def render(self):
        """Render the file manager component."""
            # Custom styling example
        st.html("""
            <style>
                /* Style the main container */
                .st-key-file_manager_container {
                    padding: unset;
                    gap: unset;
                }
                .st-key-file_manager_container .stButton button{   
                    padding: unset;
                    border: 0px;
                }
                .st-key-file_manager_container .stButton button:active{   
                    padding: unset;
                    border: 0px;
                    background-color:unset;
                    color:unset;
                }
                .st-key-file_manager_container hr{   
                    margin-top: 10px;
                }    
            </style>
        """)
        
        with st.container(border=False, key=f"{self.key_prefix}file_manager_container"):
            if st.session_state[self._get_state_key('page_content')]:
                col1, col2, colObsidian = st.columns([1,1,1])

                with colObsidian:
                    file_path = st.session_state[self._get_state_key('current_path')].replace("\\", "%2F").replace(" ", "%20")
                    st.link_button(f"📝 Obsidian", url=f"obsidian://open?path={file_path}")
            else:
                col1, col2 = st.columns([4,1])

            # New Folder Input
            with col1:
                if st.session_state[self._get_state_key('page_content')]:
                    file_name = st.session_state[self._get_state_key('current_path')].split("\\")[-1][:-3]
                    st.markdown(f"#### ***{file_name}***")
                else:
                    st.markdown(f"***{st.session_state[self._get_state_key('current_path')]}***")
            with col2:
                if st.session_state[self._get_state_key('current_path')] != self.root_path:
                    if st.button('↩️ Back', key=f"{self.key_prefix}up"):
                        st.session_state[self._get_state_key('current_path')] = str(
                            Path(st.session_state[self._get_state_key('current_path')]).parent
                        )
                        st.session_state[self._get_state_key('show_new_folder_input')] = False
                        st.session_state[self._get_state_key('current_page')] = 1
                        st.session_state[self._get_state_key('page_content')] = None
                        st.rerun()

            st.divider()

            if not st.session_state[self._get_state_key('page_content')]:
                
                # Top navigation bar
                col3, col4, col5 = st.columns([1, 1, 1])
                
                with col3:
                    with st.popover('📁 New Folder', use_container_width=True):
                        with st.container(border=False):
                            folder_name = st.text_input(
                                "Enter folder name:",
                                key=f"{self.key_prefix}new_folder_name",
                                help="Create a new folder inside the current directory."
                            )
                            col1, col2 = st.columns([1, 1])
                            with col1:
                                if st.button("Create", key=f"{self.key_prefix}create_folder"):
                                    if folder_name and folder_name.strip():
                                        if self._create_new_folder(folder_name):
                                            st.success(f"Created folder: {folder_name}")
                                            st.session_state[self._get_state_key('show_new_folder_input')] = False
                                            st.rerun()
                                    else:
                                        st.error("Please enter a folder name")
                
                with col4:
                    if st.button('📤 Upload', key=f"{self.key_prefix}upload", use_container_width=True):
                        st.session_state[self._get_state_key('show_upload')] = True
                
                with col5:
                    items_per_page = st.selectbox(
                        "Items per page",
                        options=self.items_per_page_options,
                        key=f"{self.key_prefix}items_per_page_selector",
                        label_visibility="collapsed"
                    )
                    if items_per_page != st.session_state[self._get_state_key('items_per_page')]:
                        st.session_state[self._get_state_key('items_per_page')] = items_per_page
                        st.session_state[self._get_state_key('current_page')] = 1
                        st.rerun()

                # Upload Component
                if st.session_state[self._get_state_key('show_upload')]:
                    with st.container(border=True):
                        uploaded_files = st.file_uploader(
                            "Choose files",
                            accept_multiple_files=True,
                            key=f"{self.key_prefix}file_uploader"
                        )
                        
                        col1, col2 = st.columns([1, 5])
                        with col1:
                            if st.button("Close", key=f"{self.key_prefix}close_upload"):
                                st.session_state[self._get_state_key('show_upload')] = False
                                st.session_state[self._get_state_key('upload_success')] = []
                                st.rerun()
                        
                        if uploaded_files:
                            if self._handle_file_upload(uploaded_files):
                                st.session_state[self._get_state_key('show_upload')] = False
                                st.rerun()

                st.divider()


            # File/Folder List
            items = self._get_files_and_folders()
            items.sort(key=lambda x: (not x['is_directory'], x['name'].lower()))
            
            start_idx = (st.session_state[self._get_state_key('current_page')] - 1) * st.session_state[self._get_state_key('items_per_page')]
            end_idx = start_idx + st.session_state[self._get_state_key('items_per_page')]
            paginated_items = items[start_idx:end_idx]

            if not paginated_items:
                if content := st.session_state[self._get_state_key('page_content')]:
                    st.markdown(content)
                else:
                    print("No items found!")
                    st.error("No items found !!")
            else:
                for item in paginated_items:
                    _, col1, _, col_super = st.columns([0.5, 2, 1, 1])
                    is_active = (st.session_state[self._get_state_key('previous_path')] == item['path'])
                    
                    with col1:
                        if item['is_directory']:
                            if st.button(
                                f"📁 {item['name']}", 
                                key=f"{self.key_prefix}dir_{item['path']}",
                                use_container_width=True,
                            ):
                                st.session_state[self._get_state_key('previous_path')] = \
                                    st.session_state[self._get_state_key('current_path')]
                                st.session_state[self._get_state_key('current_path')] = item['path']
                                st.session_state[self._get_state_key('show_new_folder_input')] = False
                                st.session_state[self._get_state_key('current_page')] = 1
                                st.rerun()
                        else:
                            if st.button(
                                f"📄 {item['name'][:-3]}", 
                                key=f"{self.key_prefix}file_{item['path']}",
                                use_container_width=True,
                            ):
                                st.session_state[self._get_state_key('previous_path')] = st.session_state[self._get_state_key('current_path')]
                                st.session_state[self._get_state_key('current_path')] = item['path']
                                st.session_state[self._get_state_key('show_new_folder_input')] = False
                                st.session_state[self._get_state_key('current_page')] = 1

                                with open(item['path'], 'r') as f:
                                    content = f.read()
                                    if not content:
                                        content = "# Empty File!!"
                                    st.session_state[self._get_state_key('page_content')] = content

                                st.rerun()

                    with col_super:
                        col2, col3 = st.columns([1, 1])
                        with col2:
                            if not item['is_directory']:
                                st.text(self._format_size(item['size']))
                        
                        with col3:
                            delete_button = st.button('🗑️', key=f"{self.key_prefix}del_{item['path']}", help="Delete item")
                            if f"delete_button_{item['path']}" not in st.session_state:
                                st.session_state[f"delete_button_{item['path']}"] = False
                            if delete_button:
                                st.session_state[f"delete_button_{item['path']}"] = delete_button

                    if st.session_state[f"delete_button_{item['path']}"]:
                        st.warning(f"Are you sure you want to delete {item['name']}?")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("Confirm", key=f"{item['name']}_confirm", type="primary"):
                                st.session_state[f"delete_button_{item['path']}"] = False
                                if self._delete_item(item['path']):
                                    st.rerun()
                        
                        with col2:
                            if st.button("Cancel", key=f"{item['name']}_cancel"):
                                st.session_state[f"delete_button_{item['path']}"] = False

                st.divider()
            self._render_pagination(len(items))

    @property
    def current_path(self) -> str:
        """Get current directory path."""
        return st.session_state[self._get_state_key('current_path')]

    @property
    def selected_items(self) -> List[str]:
        """Get list of selected items (for future implementation)."""
        return []  # Placeholder for future feature
    

# st.title("Vault Explorer")
file_manager = StreamlitFileManager(root_path=get_vault_path()[0], key_prefix="file_manager_")
file_manager.render()
