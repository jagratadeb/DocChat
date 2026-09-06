"""
pages/1_Architecture.py

Explains how the system works: the retrieval pipeline, what the Groq API
is used for, and how API calls are kept cheap without hurting answer
quality across multiple documents.
"""

import streamlit as st

st.set_page_config(page_title="DocChat - Architecture", layout="centered")

st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent;}
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: #0e1117; color: #e6e6e6; }
    section[data-testid="stSidebar"] { background: #12151c; border-right: 1px solid #262b36; }
    section[data-testid="stSidebar"] * { color: #d0d3da; }

    h1, h2, h3 { color: #f2f2f3 !important; font-weight: 700 !important; }
    p, li { color: #c3c7d1; }

    .section {
        background: #161a22;
        border: 1px solid #232833;
        border-radius: 10px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1.2rem;
    }
    .stage {
        border-left: 2px solid #2563eb;
        padding-left: 1rem;
        margin-bottom: 0.9rem;
    }
    .stage b { color: #e6e6e6; }

    code {
        font-family: 'JetBrains Mono', monospace !important;
        background: #1a1f2a !important;
        color: #93c5fd !important;
    }

    table { width: 100%; border-collapse: collapse; }
    th, td {
        text-align: left;
        padding: 0.5rem 0.7rem;
        border-bottom: 1px solid #232833;
        font-size: 0.88rem;
    }
    th { color: #8a8f9c; font-weight: 600; }
    td { color: #d0d3da; }
</style>
""", unsafe_allow_html=True)

st.title("Architecture")
st.caption("How DocChat retrieves, grounds, and generates answers, and what runs where.")

# ---------------------------------------------------------------------------
st.markdown('<div class="section">', unsafe_allow_html=True)
st.subheader("End-to-end pipeline")

st.markdown("""
<div class="stage"><b>1. Upload</b><br>Up to five PDF or text files are uploaded. Each file is parsed into
raw text and tagged with its filename as metadata, so every downstream chunk can always
be traced back to its source document.</div>

<div class="stage"><b>2. Chunking</b><br>Each document's text is split into overlapping chunks
(~800 characters, 100-character overlap) using a recursive character splitter. Overlap
prevents relevant sentences from being cut in half at a chunk boundary.</div>

<div class="stage"><b>3. Embedding</b><br>Every chunk is converted into a numerical vector using a
HuggingFace sentence-transformer model (<code>all-MiniLM-L6-v2</code>), which runs locally in the
app's own process. No embedding data is sent to any external API - this step is free and
has no rate limit.</div>

<div class="stage"><b>4. Indexing</b><br>Instead of one merged vector index across all documents,
DocChat builds a <b>separate FAISS index per uploaded file</b>. This is the key design decision
behind multi-document accuracy (see below).</div>

<div class="stage"><b>5. Retrieval</b><br>When a question is asked, DocChat runs a similarity
search against <i>every</i> document's index independently, then merges and ranks the results
before building the final prompt.</div>

<div class="stage"><b>6. Generation</b><br>The retrieved excerpts, labeled by source file, are
assembled into a single prompt and sent to the Groq API, which returns a natural-language
answer grounded only in that retrieved context.</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
st.markdown('<div class="section">', unsafe_allow_html=True)
st.subheader("What the Groq API is doing")

st.markdown("""
Groq does not perform retrieval, embedding, or indexing in this system - all of that
happens locally, for free, before Groq is ever called. Groq's only job is the final
**generation step**: given a question and a set of retrieved excerpts, produce a
coherent, natural-language answer.

Groq is used here (instead of running a local LLM) because:
""")

st.markdown("""
| Reason | Detail |
|---|---|
| Speed | Groq runs open-weight models on custom inference hardware (LPUs), returning answers in a fraction of a second even for large contexts. |
| Free tier | No cost for moderate usage, which matches this project's zero-budget deployment goal. |
| No local GPU needed | Generation would otherwise require a GPU-hosted model; Groq removes that requirement entirely. |
| Model choice | Groq hosts several open-weight models (Llama, GPT-OSS, Qwen) that can be swapped by changing one config value. |
""")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
st.markdown('<div class="section">', unsafe_allow_html=True)
st.subheader("Optimizing API calls without losing quality")

st.markdown("""
Two problems had to be solved at once: keep the number of tokens sent to Groq on every
question small and predictable, while still giving the model a fair, complete view
across every uploaded document.

**The naive approach (one shared index):** put every chunk from every document into a
single FAISS index and retrieve the top-k most similar chunks overall. This is what
DocChat originally did. It fails silently when documents are similar to each other -
for example, three resumes each containing an "Education" section. If two resumes'
Education sections are worded more closely to the question than the third, all of the
top-k slots get filled by those two, and the third resume's Education section is never
retrieved at all. The model isn't wrong; it was simply never shown the relevant text.

**DocChat's approach (per-source retrieval):** a separate FAISS index is kept per
document. On every question, a small, fixed number of chunks
(currently 2) is retrieved from **each** document's index independently, then all of
those results are merged into one prompt. This guarantees every uploaded file gets a
chance to contribute to the answer, regardless of how similar its wording is to any
other file.

**Why this doesn't blow up cost:** the total context size is capped at
`max files (5) x chunks per file (2) = 10 chunks` in the worst case - actually smaller
in most sessions, since most users upload fewer than five files. This is a fixed,
predictable ceiling on prompt size and therefore on Groq token usage per question,
regardless of how large the underlying documents are. Compare this to naively
increasing k on a shared index to "be safe," which scales token cost with the total
number of documents and offers no real guarantee of per-document coverage.

**Other quality levers, without added Groq cost:**
""")

st.markdown("""
- Chunk overlap (100 characters) reduces the chance a key fact is split across a chunk
  boundary and only half-retrieved.
- A low generation temperature (0.1) favors literal, grounded answers over creative
  phrasing, reducing the chance of the model drifting from the retrieved context.
- The prompt instructs the model to explicitly say when an answer isn't present in the
  retrieved context, rather than guessing - this costs nothing extra per call but
  meaningfully reduces hallucinated answers.
""")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
st.markdown('<div class="section">', unsafe_allow_html=True)
st.subheader("Security notes")

st.markdown("""
- The Groq API key is read from Streamlit secrets (when deployed) or a local `.env` file
  (never committed to source control - see `.gitignore`), and is never printed, logged,
  or displayed anywhere in the UI.
- If no key is configured, the app asks for one via a password-masked input field held
  only in that browser session's memory; it is not written to disk.
- Uploaded documents are processed in memory and temporary files for the duration of the
  session only. Nothing is persisted between sessions or shared across users.
""")
st.markdown('</div>', unsafe_allow_html=True)
