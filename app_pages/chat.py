"""
app_pages/chat.py

Main chat interface for the AI Document Q&A Assistant.
"""

import os
import streamlit as st
from dotenv import load_dotenv

from styles import inject_app_footer, inject_app_header, inject_base_styles
from rag_pipeline import (
    load_documents,
    build_vectorstores,
    build_llm,
    answer_question,
    format_source_label,
    MAX_FILES,
    CHUNKS_PER_SOURCE,
)

load_dotenv()
inject_base_styles()
inject_app_header()


def get_groq_api_key():
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    return os.getenv("GROQ_API_KEY", "")


GROQ_API_KEY = get_groq_api_key()

if "vectorstores" not in st.session_state:
    st.session_state.vectorstores = None
if "llm" not in st.session_state:
    st.session_state.llm = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "doc_names" not in st.session_state:
    st.session_state.doc_names = []
if "num_chunks" not in st.session_state:
    st.session_state.num_chunks = 0
if "processing_complete" not in st.session_state:
    st.session_state.processing_complete = False

# ---------------------------------------------------------------------------
# Sidebar — session and file details. Uploading stays in the main workspace so
# the primary action remains available on narrow screens.
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("""
    <div class="brand-row">
        <span class="brand-mark">&lt;/&gt;</span>
        <span class="brand-name">DocChat</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-kicker">This visit</div>', unsafe_allow_html=True)
    if not GROQ_API_KEY:
        manual_key = st.text_input("Groq access key", type="password", placeholder="gsk_...")
        if manual_key:
            GROQ_API_KEY = manual_key
        st.caption("Needed to create answers.")

    if st.session_state.doc_names:
        st.markdown('<div class="sidebar-kicker">Your files</div>', unsafe_allow_html=True)
        st.markdown(f"<div class='metric-grid'><div class='metric'><strong>{len(st.session_state.doc_names)}</strong><span>files</span></div><div class='metric'><strong>{len(st.session_state.chat_history)}</strong><span>answers</span></div></div>", unsafe_allow_html=True)
        for name in st.session_state.doc_names:
            st.markdown(f"<div class='doc-chip'>{name}</div>", unsafe_allow_html=True)
        st.caption(f"We check up to {CHUNKS_PER_SOURCE} parts of each file for every question.")
        st.write("")
        if st.button("Remove files and answers", use_container_width=True):
            st.session_state.vectorstores = None
            st.session_state.llm = None
            st.session_state.doc_names = []
            st.session_state.num_chunks = 0
            st.session_state.chat_history = []
            st.session_state.processing_complete = False
            st.rerun()
    else:
        st.markdown('<div class="sidebar-kicker">Your files</div>', unsafe_allow_html=True)
        st.caption("No files added yet. Add them below to begin.")

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------

st.markdown("""
<div class="hero">
    <h1>Ask anything about your <span class="accent">files</span></h1>
    <p>Upload up to five files and get answers based on their contents, with the file and page shown for every response.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="upload-panel">
    <h3>Add your files</h3>
    <p>Choose up to 5 PDF, TXT, or Markdown files. <strong>Only 5 files are allowed per visit.</strong></p>
</div>
""", unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "Choose up to 5 files",
    type=["pdf", "txt", "md"],
    accept_multiple_files=True,
    label_visibility="visible",
)

if uploaded_files and len(uploaded_files) > MAX_FILES:
    st.error(f"Please select at most {MAX_FILES} files (you selected {len(uploaded_files)}).")
elif uploaded_files and st.button("Read my files", use_container_width=True, type="primary"):
    if not GROQ_API_KEY:
        st.error("Please add your Groq access key in the panel first.")
    else:
        with st.spinner(f"Reading {len(uploaded_files)} file(s)..."):
            try:
                documents = load_documents(uploaded_files)
                vectorstores, num_chunks = build_vectorstores(documents)
                llm = build_llm(GROQ_API_KEY)

                st.session_state.vectorstores = vectorstores
                st.session_state.llm = llm
                st.session_state.doc_names = [f.name for f in uploaded_files]
                st.session_state.num_chunks = num_chunks
                st.session_state.chat_history = []
                st.session_state.processing_complete = True

                st.toast(f"Your {len(uploaded_files)} file(s) are ready.")
                st.rerun()
            except Exception as e:
                st.error(f"Could not process those files: {e}")

if st.session_state.processing_complete and st.session_state.llm:
    st.markdown(
        '<div class="processing-complete"><strong>Documents are ready.</strong> You can chat now.</div>',
        unsafe_allow_html=True,
    )

if not st.session_state.llm:
    st.markdown("""
    <div class="empty-state">
        <h3>No files added</h3>
        <p>Add up to five PDF or text files above, then select Read my files.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    for question, answer, sources in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant"):
            st.write(answer)
            if sources:
                with st.expander("Where this answer came from"):
                    for i, doc in enumerate(sources, 1):
                        st.markdown(f"**{format_source_label(doc, i)}**")
                        st.text(doc.page_content[:500] + ("..." if len(doc.page_content) > 500 else ""))

    question = st.chat_input("Ask a question about your documents")

    if question:
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Finding the answer..."):
                try:
                    answer, sources = answer_question(
                        st.session_state.llm, st.session_state.vectorstores, question
                    )
                    st.write(answer)
                    if sources:
                        with st.expander("Where this answer came from"):
                            for i, doc in enumerate(sources, 1):
                                st.markdown(f"**{format_source_label(doc, i)}**")
                                st.text(doc.page_content[:500] + ("..." if len(doc.page_content) > 500 else ""))
                    st.session_state.chat_history.append((question, answer, sources))
                except Exception as e:
                    st.error(f"Something went wrong: {e}")

inject_app_footer()
