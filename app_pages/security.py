"""
app_pages/security.py

Plain-language explanation of DocChat's privacy and security behavior.
"""

import streamlit as st

from styles import inject_app_footer, inject_app_header, inject_base_styles

inject_base_styles()
inject_app_header()

st.markdown(
    """
    <div class="hero">
        <h1>Privacy <span class="accent">& security</span></h1>
        <p>Here is what happens to your files and questions, explained simply.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.warning(
    "Please do not upload highly confidential or sensitive files unless you have "
    "checked your hosting service's and Groq's privacy rules."
)

st.error(
    "Important responsibility notice: DocChat and its operators are not responsible "
    "for any leak, loss, or unauthorized access involving uploaded files."
)

st.markdown(
    """
    <div class="section-card">
        <h3>What happens to an uploaded file?</h3>
        <p>Your file is read for this visit. DocChat briefly makes a local copy to read
        it, then removes that copy. The text is split into small parts and kept while
        you are using the app so you can ask questions.</p>
        <p>DocChat does not intentionally save your original file in a permanent database.
        The current app does not provide accounts or long-term document storage.</p>
    </div>

    <div class="section-card">
        <h3>What information goes to Groq?</h3>
        <p>When you ask a question, DocChat sends Groq:</p>
        <ul>
            <li>Your question.</li>
            <li>The relevant parts of your uploaded files.</li>
            <li>The file name and page information for those parts.</li>
        </ul>
        <p>The complete original file is not intentionally sent. However, a part of the
        file can contain sensitive information if that information appears in it.</p>
    </div>

    <div class="section-card">
        <h3>What does Groq do with it?</h3>
        <p>Groq uses the question and relevant file parts to generate your answer. Groq is a separate
        company, so its retention, monitoring, training, and deletion rules are controlled
        by Groq's own policies. DocChat cannot promise how long Groq or the hosting platform
        keeps request logs.</p>
        <p>Check Groq's current privacy and data-use terms before uploading sensitive content.</p>
    </div>

    <div class="section-card">
        <h3>What stays inside this app?</h3>
        <ul>
            <li>Reading your files and splitting their text into small parts.</li>
            <li>Searching your files on the app's computer.</li>
            <li>Your current files and chat history while you are here.</li>
        </ul>
        <p>Use <strong>Remove files and answers</strong> on the Chat page to clear your
        current files and chat history.</p>
    </div>

    <div class="section-card">
        <h3>How is the Groq access key handled?</h3>
        <p>The Groq access key is read from the app's private settings or the password-protected
        key field. DocChat does not intentionally display or log it.
        Never share or commit a real access key.</p>
    </div>

    <div class="section-card">
        <h3>Simple safety advice</h3>
        <ul>
            <li>Upload only the files needed for your question.</li>
            <li>Remove passwords, access tokens, and private identifiers first.</li>
            <li>Use a trusted secure website for anything beyond local testing.</li>
            <li>Remember that this app has no sign-in or separate file access for each user.</li>
        </ul>
    </div>

    <div class="section-card">
        <h3>Who is responsible for protecting your files?</h3>
        <p>You are responsible for deciding what to upload and where you use this site.
        The hosting service, Groq, internet providers, and other services may have their
        own systems and rules. DocChat cannot control or guarantee their security.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

inject_app_footer()
