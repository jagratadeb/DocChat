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
    layout="centered",
    initial_sidebar_state="expanded",
)

chat_page = st.Page("app_pages/chat.py", title="Chat", default=True)
architecture_page = st.Page("app_pages/architecture.py", title="Architecture")

pg = st.navigation([chat_page, architecture_page], position="top")
pg.run()
