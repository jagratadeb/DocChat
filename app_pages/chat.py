"""
app_pages/chat.py

Main chat interface for the AI Document Q&A Assistant.
"""

import os
import streamlit as st
from dotenv import load_dotenv

from styles import inject_base_styles
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

# ---------------------------------------------------------------------------
# Sidebar — documents only, no navigation here
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("""
    <div class="brand-row">
        <span class="brand-mark">&lt;/&gt;</span>
        <span class="brand-name">DocChat</span>
    </div>
    """, unsafe_allow_html=True)

    if not GROQ_API_KEY:
        manual_key = st.text_input("Groq API key", type="password", placeholder="gsk_...")
        if manual_key:
            GROQ_API_KEY = manual_key
        st.caption("Get a free key at console.groq.com")

    st.markdown("**Documents**")
    uploaded_files = st.file_uploader(
        f"Up to {MAX_FILES} files, PDF / TXT / MD",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files and len(uploaded_files) > MAX_FILES:
        st.error(f"Please select at most {MAX_FILES} files (you selected {len(uploaded_files)}).")
    elif uploaded_files and st.button("Process documents", use_container_width=True, type="primary"):
        if not GROQ_API_KEY:
            st.error("Please add a Groq API key first.")
        else:
            with st.spinner(f"Indexing {len(uploaded_files)} file(s)..."):
                try:
                    documents = load_documents(uploaded_files)
                    vectorstores, num_chunks = build_vectorstores(documents)
                    llm = build_llm(GROQ_API_KEY)

                    st.session_state.vectorstores = vectorstores
                    st.session_state.llm = llm
                    st.session_state.doc_names = [f.name for f in uploaded_files]
                    st.session_state.chat_history = []

                    st.toast(f"Indexed {num_chunks} chunks across {len(uploaded_files)} file(s).")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not process those files: {e}")

    if st.session_state.doc_names:
        st.markdown("**Active**")
        chips = "".join(f'<span class="doc-chip">{name}</span>' for name in st.session_state.doc_names)
        st.markdown(chips, unsafe_allow_html=True)
        st.caption(f"Up to {CHUNKS_PER_SOURCE} excerpts retrieved per document, per question.")
        st.write("")
        if st.button("Clear session", use_container_width=True):
            st.session_state.vectorstores = None
            st.session_state.llm = None
            st.session_state.doc_names = []
            st.session_state.chat_history = []
            st.rerun()

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------

st.markdown("""
<div class="hero">
    <h1>Ask your <span class="accent">documents</span> anything</h1>
    <p>Upload up to five files and get answers grounded in their actual content, with sources shown for every response.</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.llm:
    st.markdown("""
    <div class="empty-state">
        <h3>No documents loaded</h3>
        <p>Upload up to five PDF or text files from the sidebar, then click Process documents.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    for question, answer, sources in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant"):
            st.write(answer)
            if sources:
                with st.expander("Sources"):
                    for i, doc in enumerate(sources, 1):
                        st.markdown(f"**{format_source_label(doc, i)}**")
                        st.text(doc.page_content[:500] + ("..." if len(doc.page_content) > 500 else ""))

    question = st.chat_input("Ask a question about your documents")

    if question:
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Retrieving and generating an answer..."):
                try:
                    answer, sources = answer_question(
                        st.session_state.llm, st.session_state.vectorstores, question
                    )
                    st.write(answer)
                    if sources:
                        with st.expander("Sources"):
                            for i, doc in enumerate(sources, 1):
                                st.markdown(f"**{format_source_label(doc, i)}**")
                                st.text(doc.page_content[:500] + ("..." if len(doc.page_content) > 500 else ""))
                    st.session_state.chat_history.append((question, answer, sources))
                except Exception as e:
                    st.error(f"Something went wrong: {e}")
