"""
app_pages/home.py

Landing page for DocChat. The document workflow starts on the dedicated chat page.
"""

import streamlit as st

from styles import inject_app_footer, inject_base_styles

inject_base_styles()

st.markdown(
    """
    <div class="landing-grid">
        <main class="landing-hero">
            <div class="landing-eyebrow">CLEAR ANSWERS FROM YOUR FILES</div>
            <h1>Turn your files into a <span class="accent">conversation.</span></h1>
            <p class="landing-lede">Upload the files that matter, ask questions in your own words, and get answers linked to the files they came from.</p>
        </main>
        <aside class="landing-preview" aria-label="Document workspace preview">
            <div class="preview-head">
                <span class="preview-kicker">YOUR FILES</span>
                <span class="preview-live"><i></i> READY TO READ</span>
            </div>
            <div class="preview-title">One place for every file.</div>
            <div class="preview-files">
                <div class="preview-row"><span class="file-icon pdf">PDF</span><span>research-notes.pdf</span></div>
                <div class="preview-row"><span class="file-icon txt">TXT</span><span>project-brief.txt</span></div>
                <div class="preview-row"><span class="file-icon md">MD</span><span>meeting-summary.md</span></div>
            </div>
            <div class="preview-foot"><span>ANSWERS LINKED TO YOUR FILES</span></div>
        </aside>
    </div>
    """,
    unsafe_allow_html=True,
)

action_column, _ = st.columns([1.15, 0.85])
with action_column:
    if st.button("Start Chatting", type="primary"):
        st.switch_page("app_pages/chat.py")

st.markdown(
    """
    <section class="landing-features">
        <article>
            <div class="feature-number">01</div>
            <h3>Bring your files</h3>
            <p>Work with up to five PDF, TXT, or Markdown files in one place.</p>
        </article>
        <article>
            <div class="feature-number">02</div>
            <h3>Ask naturally</h3>
            <p>Ask in your own words instead of searching through pages yourself.</p>
        </article>
        <article>
            <div class="feature-number">03</div>
            <h3>See where answers came from</h3>
            <p>Every answer shows the file and page parts used to answer you.</p>
        </article>
    </section>
    """,
    unsafe_allow_html=True,
)

inject_app_footer()
