# STREAMLIT
import streamlit as st
from streamlit_extras.grid import grid
from streamlit_extras.app_logo import add_logo


# --- PAGE CONFIG (BROWSER TAB) ---
st.set_page_config(page_title="Sharktank", page_icon=":shark:", layout="centered", initial_sidebar_state="expanded")


# ---- LOAD ASSETS ----
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
local_css("style/style.css")


# --- MAIN PAGE ---
with st.container():
        st.title("Fuck Banks")
        st.info("Nothing to see here!")
        pass