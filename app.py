"""
app.py

Entry point. Defines top-level navigation (Chat, Architecture) using
Streamlit's page-based navigation, rendered as a top nav bar rather than
inside the sidebar - the sidebar is reserved for document controls only.
"""

import streamlit as st

st.set_page_config(
    page_title="DocChat",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

home_page = st.Page("app_pages/home.py", title="Home", default=True)
chat_page = st.Page("app_pages/chat.py", title="Chat")
architecture_page = st.Page("app_pages/architecture.py", title="Architecture")
security_page = st.Page("app_pages/security.py", title="Privacy & Security")

pg = st.navigation([home_page, chat_page, architecture_page, security_page], position="top")
pg.run()
