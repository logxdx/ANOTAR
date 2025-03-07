import streamlit as st
from st_pages import get_nav_from_toml

st.logo("pages/note.png")
nav = get_nav_from_toml(".streamlit/pages_sections.toml")
pg = st.navigation(nav)
pg.run()