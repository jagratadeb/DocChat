"""
styles.py

Shared CSS for a modern, dark, responsive UI across all pages.
"""

import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()


SOCIAL_LINKS = {
    "LinkedIn": os.getenv("DOCCHAT_LINKEDIN_URL", ""),
    "GitHub": os.getenv("DOCCHAT_GITHUB_URL", ""),
    "X": os.getenv("DOCCHAT_X_URL", ""),
    "Bluesky": os.getenv("DOCCHAT_BLUESKY_URL", ""),
}

BASE_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
    #MainMenu {visibility: hidden;}
    footer:not(.app-footer) {visibility: hidden;}
    header[data-testid="stHeader"] {
        background: rgba(6, 8, 13, 0.85);
        backdrop-filter: blur(8px);
        border-bottom: 1px solid #1c212b;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    *, *::before, *::after { box-sizing: border-box; }
    html, body, .stApp { max-width: 100%; overflow-x: hidden; }

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
    section[data-testid="stSidebar"] > div:first-child { padding-top: 1.25rem; }
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

    .app-topbar {
        padding: 0.35rem 0 0.85rem;
        border-bottom: 1px solid #1c212b;
        margin-bottom: 0.3rem;
    }
    .app-title {
        color: #f5f6f8;
        font-size: 1rem;
        font-weight: 800;
        letter-spacing: 0.01em;
        white-space: nowrap;
    }
    .social-links {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.4rem 0.8rem;
    }
    .social-links a,
    .social-links span {
        color: #8b93a3 !important;
        font-size: 0.76rem;
        text-decoration: none;
    }
    .social-links a:hover { color: #34d399 !important; }
    .app-footer {
        border-top: 1px solid #1c212b;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin-top: 3rem;
        padding: 1.15rem 0 0.5rem;
    }
    .footer-credit {
        color: #7f899b;
        font-size: 0.78rem;
        margin: 0;
    }
    .footer-links {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    .footer-link {
        align-items: center;
        background: #10141c;
        border: 1px solid #252d3b;
        border-radius: 7px;
        color: #c7cbd4 !important;
        display: inline-flex;
        font-size: 0.76rem;
        gap: 0.38rem;
        padding: 0.35rem 0.55rem;
        text-decoration: none;
    }
    .footer-link:hover { border-color: #34d399; color: #34d399 !important; }
    .social-icon {
        align-items: center;
        border: 1px solid #536074;
        border-radius: 4px;
        color: #e7e9ee;
        display: inline-flex;
        font-size: 0.62rem;
        font-weight: 800;
        height: 1.05rem;
        justify-content: center;
        letter-spacing: -0.02em;
        line-height: 1;
        min-width: 1.05rem;
        padding: 0 0.12rem;
    }
    .processing-complete {
        background: #0d2b22;
        border: 1px solid #1d6049;
        border-radius: 10px;
        color: #a7f3d0;
        font-size: 0.9rem;
        line-height: 1.45;
        margin: 0.2rem 0 1rem;
        padding: 0.75rem 0.9rem;
    }

    .sidebar-kicker {
        color: #7f899b;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.09em;
        text-transform: uppercase;
        margin: 1.1rem 0 0.45rem;
    }
    .upload-panel {
        background: rgba(16, 20, 28, 0.86);
        border: 1px solid #252d3b;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.3rem 0 1.4rem;
    }
    .upload-panel h3 {
        color: #f5f6f8;
        font-size: 1rem;
        margin: 0 0 0.25rem;
    }
    .upload-panel p {
        color: #8b93a3;
        font-size: 0.84rem;
        margin: 0;
    }
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.5rem;
        margin: 0.75rem 0;
    }
    .metric {
        background: #10141c;
        border: 1px solid #1f2531;
        border-radius: 8px;
        padding: 0.65rem;
        min-width: 0;
    }
    .metric strong { display: block; color: #f5f6f8; font-size: 1.05rem; }
    .metric span { color: #7f899b; font-size: 0.72rem; }

    .hero {
        padding: 1.5rem 0 1.2rem 0;
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
    .architecture-image {
        background: #0b0e14;
        border: 1px solid #252d3b;
        border-radius: 12px;
        padding: 0.75rem;
        margin-bottom: 1.2rem;
    }
    .architecture-image img { max-width: 100%; height: auto; }
    .technical-table { overflow-x: auto; max-width: 100%; }
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
        section[data-testid="stSidebar"] { width: min(86vw, 21rem) !important; }
        section[data-testid="stSidebar"] > div:first-child { padding: 1rem 0.8rem; }
        div[data-testid="stMainBlockContainer"] { padding: 0 0.85rem 2rem; }
        .hero { padding: 1.2rem 0 1rem 0; }
        .hero h1 { font-size: 1.5rem; }
        .hero p { font-size: 0.88rem; }
        .section-card { padding: 1rem; }
        div[data-testid="stChatMessage"] { padding: 0.5rem 0.7rem; }
        .upload-panel { padding: 0.85rem; }
        .app-footer { align-items: flex-start; flex-direction: column; gap: 0.75rem; }
        .footer-links { gap: 0.4rem; }
        table { min-width: 34rem; }
    }
    @media (min-width: 641px) {
        button[data-testid="stSidebarCollapseButton"] { display: none !important; }
    }
</style>
"""


def inject_base_styles():
    st.markdown(BASE_CSS, unsafe_allow_html=True)


def inject_app_header():
    st.markdown(
        """
        <div class="app-topbar">
            <div class="app-title">DocChat</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def inject_app_footer():
    icon_labels = {
        "LinkedIn": "in",
        "GitHub": "GH",
        "X": "X",
        "Bluesky": "BS",
    }
    links = "".join(
        f'<a class="footer-link" href="{url}" target="_blank" '
        f'rel="noopener noreferrer" aria-label="Open {label}">'
        f'<span class="social-icon" aria-hidden="true">{icon_labels[label]}</span>{label}</a>'
        for label, url in SOCIAL_LINKS.items()
        if url
    )
    link_markup = links or '<span class="footer-credit">Add profile URLs in your .env file</span>'
    st.markdown(
        f"""
        <footer class="app-footer">
            <p class="footer-credit">Developed by Jagrata Deb</p>
            <nav class="footer-links" aria-label="Social links">{link_markup}</nav>
        </footer>
        """,
        unsafe_allow_html=True,
    )
