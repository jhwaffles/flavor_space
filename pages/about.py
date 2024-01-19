from pathlib import Path
import streamlit as st
import numpy as np

#cluster browser portion
st.header("About")

def read_markdown_file(markdown_file):
    print(Path(markdown_file).read_text())
    return Path(markdown_file).read_text()

intro_markdown = read_markdown_file("about.md")
st.markdown(intro_markdown)