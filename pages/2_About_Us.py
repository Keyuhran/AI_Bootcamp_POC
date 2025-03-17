# pages/2_About_Us.py
import streamlit as st
from pathlib import Path
from nav_modules.nav import MenuButtons
from pages.Account import get_roles

MenuButtons(get_roles())

def read_markdown_file(markdown_file):
    return Path(markdown_file).read_text()

intro_markdown = read_markdown_file("data/About_Us_WriteUp.md")
st.markdown(intro_markdown, unsafe_allow_html=True)