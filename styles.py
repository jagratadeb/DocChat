"""
styles.py

Shared CSS for a modern, dark, responsive UI across all pages, styled to
match a portfolio-site aesthetic: dark background, teal/blue gradient
accents, pill-shaped buttons, and a clean top navigation bar.
"""

import streamlit as st

BASE_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {
        background: rgba(6, 8, 13, 0.85);
        backdrop-filter: blur(8px);
        border-bottom: 1px solid #1c212b;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at 80% 0%, #0d1720 0%, #06080d 55%);
        color: #e7e9ee;
    }

    div[data-testid="stTabs"] button,
    div[role="tablist"] button {
        font-weight: 500;
        color: #9aa0ac !important;
    }

    section[data-testid="stSidebar"] {
        background: #0b0e14;
        border-right: 1px solid #1c212b;
    }
    section[data-testid="stSidebar"] * {
        color: #c7cbd4;
    }

    .brand-row {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.2rem 0 1rem 0;
        border-bottom: 1px solid #1c212b;
        margin-bottom: 1rem;
    }
    .brand-mark {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 1rem;
        color: #34d399;
    }
    .brand-name {
        font-size: 0.85rem;
        font-weight: 600;
        color: #e7e9ee;
        letter-spacing: 0.01em;
    }

    .hero {
        padding: 2rem 0 1.6rem 0;
        margin-bottom: 1rem;
    }
    .hero h1 {
        font-size: clamp(1.8rem, 4vw, 2.6rem);
        font-weight: 800;
        letter-spacing: -0.02em;
        margin-bottom: 0.4rem;
        color: #f5f6f8;
        line-height: 1.15;
    }
    .hero .accent {
        background: linear-gradient(90deg, #34d399, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero p {
        color: #8b93a3;
        font-size: 1rem;
        max-width: 46rem;
        margin: 0;
    }

    div[data-testid="stChatMessage"] {
        background: #10141c;
        border: 1px solid #1f2531;
        border-radius: 14px;
        padding: 0.7rem 1rem;
        margin-bottom: 0.7rem;
    }

    .doc-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        background: #0f2a20;
        color: #6ee7b7;
        border-radius: 999px;
        padding: 5px 12px;
        font-size: 0.78rem;
        margin: 2px 6px 2px 0;
        border: 1px solid #1c4532;
        font-family: 'JetBrains Mono', monospace;
    }

    .empty-state {
        text-align: center;
        padding: 4.5rem 1rem 2rem 1rem;
        color: #6b7280;
    }
    .empty-state h3 {
        color: #d8dbe3;
        font-weight: 700;
        font-size: 1.2rem;
        margin-bottom: 0.4rem;
    }
    .empty-state p {
        color: #6b7280;
        font-size: 0.92rem;
    }

    div[data-testid="stChatInput"] textarea {
        background: #10141c !important;
        border: 1px solid #232a38 !important;
        border-radius: 14px !important;
        color: #e7e9ee !important;
        font-family: 'Inter', sans-serif !important;
    }
    div[data-testid="stChatInput"]:focus-within textarea {
        border-color: #34d399 !important;
    }

    .stButton>button {
        border-radius: 999px;
        font-weight: 600;
        border: 1px solid #232a38;
        background: #131822;
        color: #e7e9ee;
        padding: 0.5rem 1.1rem;
        transition: all 0.15s ease;
    }
    .stButton>button:hover {
        border-color: #34d399;
        color: #34d399;
    }
    .stButton>button[kind="primary"] {
        background: linear-gradient(90deg, #10b981, #3b82f6);
        border: none;
        color: #06080d;
    }
    .stButton>button[kind="primary"]:hover {
        opacity: 0.9;
        color: #06080d;
    }

    section[data-testid="stFileUploaderDropzone"] {
        background: #10141c;
        border: 1px dashed #232a38;
        border-radius: 12px;
    }

    code, pre, .stCodeBlock {
        font-family: 'JetBrains Mono', monospace !important;
    }

    .section-card {
        background: #10141c;
        border: 1px solid #1f2531;
        border-radius: 14px;
        padding: 1.3rem 1.5rem;
        margin-bottom: 1.2rem;
    }
    .stage {
        border-left: 2px solid #34d399;
        padding-left: 1rem;
        margin-bottom: 0.9rem;
    }
    .stage b { color: #e7e9ee; }

    table { width: 100%; border-collapse: collapse; }
    th, td {
        text-align: left;
        padding: 0.5rem 0.7rem;
        border-bottom: 1px solid #1f2531;
        font-size: 0.88rem;
    }
    th { color: #8b93a3; font-weight: 600; }
    td { color: #c7cbd4; }

    @media (max-width: 640px) {
        .hero { padding: 1.2rem 0 1rem 0; }
        .hero h1 { font-size: 1.5rem; }
        .hero p { font-size: 0.88rem; }
        .section-card { padding: 1rem; }
        div[data-testid="stChatMessage"] { padding: 0.5rem 0.7rem; }
    }
</style>
"""


def inject_base_styles():
    st.markdown(BASE_CSS, unsafe_allow_html=True)
