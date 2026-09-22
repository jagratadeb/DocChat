"""
app_pages/architecture.py

Explains how the system works: the retrieval pipeline, what the Groq API
is used for, and how API calls are kept cheap without hurting answer
quality across multiple documents.
"""

import streamlit as st
from styles import inject_base_styles

inject_base_styles()

st.markdown("""
<div class="hero">
    <h1>System <span class="accent">architecture</span></h1>
    <p>How DocChat retrieves, grounds, and generates answers, and what runs where.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("End-to-end pipeline")
st.markdown("""
<div class="stage"><b>1. Upload</b><br>Up to five PDF or text files are uploaded. Each file is parsed into
raw text and tagged with its filename as metadata, so every downstream chunk can always
be traced back to its source document.</div>

<div class="stage"><b>2. Chunking</b><br>Each document's text is split into overlapping chunks
(1000 characters, 250-character overlap) using a recursive character splitter. The overlap
is intentionally generous so a heading and the paragraph that follows it are unlikely to be
separated into different chunks - a fix for exactly the kind of "Summary" heading vs. content
gap that can otherwise cause a real answer to go unretrieved.</div>

<div class="stage"><b>3. Embedding</b><br>Every chunk is converted into a numerical vector using a
HuggingFace sentence-transformer model (all-MiniLM-L6-v2), which runs locally in the
app's own process. No embedding data is sent to any external API - this step is free and
has no rate limit.</div>

<div class="stage"><b>4. Indexing</b><br>Instead of one merged vector index across all documents,
DocChat builds a separate FAISS index per uploaded file. This is the key design decision
behind multi-document accuracy (see below).</div>

<div class="stage"><b>5. Retrieval</b><br>When a question is asked, DocChat runs a similarity
search against every document's index independently, then merges and ranks the results
before building the final prompt.</div>

<div class="stage"><b>6. Generation</b><br>The retrieved excerpts, labeled by source file, are
assembled into a single prompt and sent to the Groq API, which returns a natural-language
answer grounded only in that retrieved context.</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.image(
  "docchat_architecture_detailed.png",
  caption="DocChat indexing and per-question retrieval flow",
  use_column_width=True,
)

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("What the Groq API is doing")
st.markdown("""
Groq does not perform retrieval, embedding, or indexing in this system - all of that
happens locally, for free, before Groq is ever called. Groq's only job is the final
generation step: given a question and a set of retrieved excerpts, produce a coherent,
natural-language answer.
""")
st.markdown("""
| Reason | Detail |
|---|---|
| Speed | Groq runs open-weight models on custom inference hardware, returning answers in a fraction of a second even for large contexts. |
| Free tier | No cost for moderate usage, matching this project's zero-budget deployment goal. |
| No local GPU needed | Generation would otherwise require a GPU-hosted model; Groq removes that requirement entirely. |
| Model choice | Groq hosts several open-weight models that can be swapped by changing one config value. |
""")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("Optimizing API calls without losing quality")
st.markdown("""
**The naive approach (one shared index):** put every chunk from every document into a
single FAISS index and retrieve the top-k most similar chunks overall. This fails
silently when documents are worded similarly - for example, three resumes each with an
"Education" section. If two resumes' sections score closer to the question than the
third, all top-k slots get filled by those two, and the third resume's matching content
is never retrieved at all.

**DocChat's approach (per-source retrieval):** a separate FAISS index is kept per
document. On every question, a small, fixed number of chunks is retrieved from each
document's index independently, then merged into one prompt - guaranteeing every
uploaded file gets a chance to contribute, regardless of how similar its wording is to
any other file.

**Why this doesn't blow up cost:** total context is capped at
`max files (5) x chunks per file (3) = 15 chunks` in the worst case - fewer in most
sessions. This is a fixed, predictable ceiling on prompt size and Groq token usage per
question, regardless of how large the underlying documents are.

**Other quality levers, at no added Groq cost:**
- Generous chunk overlap reduces the chance a key fact is split across a boundary.
- A low generation temperature (0.1) favors literal, grounded answers.
- The prompt explicitly instructs the model to say when an answer isn't present in the
  retrieved context, rather than guessing.
""")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("Security notes")
st.markdown("""
- The Groq API key is read from Streamlit secrets (when deployed) or a local `.env` file
  (never committed - see `.gitignore`), and is never printed, logged, or displayed in the UI.
- If no key is configured, the app asks for one via a password-masked field held only in
  that browser session's memory; it is never written to disk.
- Uploaded documents are processed in memory for the session only. Nothing persists
  between sessions or is shared across users.
""")
st.markdown('</div>', unsafe_allow_html=True)
