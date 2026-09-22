"""
app_pages/architecture.py

Explains how the system works: the retrieval pipeline, what the Groq API
is used for, and how API calls are kept cheap without hurting answer
quality across multiple documents.
"""

import streamlit as st
from styles import inject_app_footer, inject_app_header, inject_base_styles

inject_base_styles()
inject_app_header()

st.markdown("""
<div class="hero">
    <h1>System <span class="accent">architecture</span></h1>
    <p>How DocChat retrieves, grounds, and generates answers, and what runs where.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="architecture-image">', unsafe_allow_html=True)
st.image("docchat_architecture_detailed.png", caption="Indexing and per-question retrieval flow")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("Runtime pipeline")
st.markdown("""
<div class="technical-table"><table>
<tr><th>Stage</th><th>Implementation</th><th>Output / contract</th></tr>
<tr><td>Ingestion</td><td><code>PyPDFLoader</code> or <code>TextLoader</code></td><td>LangChain documents with <code>source_file</code> metadata</td></tr>
<tr><td>Chunking</td><td><code>RecursiveCharacterTextSplitter</code>, 1,000 chars / 250 overlap</td><td>Overlapping chunks that preserve local context</td></tr>
<tr><td>Embedding</td><td><code>all-MiniLM-L6-v2</code> via Hugging Face, local process</td><td>Dense vectors; no embedding API request</td></tr>
<tr><td>Indexing</td><td>One FAISS index per source file</td><td><code>dict[str, FAISS]</code>, isolated retrieval namespaces</td></tr>
<tr><td>Retrieval</td><td>Similarity search against every index, <code>k=3</code> per file</td><td>At most 15 ranked excerpts for five files</td></tr>
<tr><td>Generation</td><td>Groq <code>openai/gpt-oss-120b</code>, temperature <code>0.1</code></td><td>Answer constrained to labeled retrieved context</td></tr>
</table></div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

inject_app_footer()

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("Design decisions and boundaries")
st.markdown("""
The application has two distinct execution boundaries. Ingestion, chunking, embedding,
and FAISS indexing run locally in the Streamlit process. Only the final question plus
the capped set of retrieved excerpts is sent to Groq for generation. Groq therefore does
not choose documents or retrieve vectors; it receives a prepared context and produces
the answer.
""")
st.markdown("""
| Constraint | Implementation |
|---|---|
| Retrieval fairness | Per-file indexes guarantee every uploaded source can contribute excerpts. |
| Context ceiling | Five files x three excerpts = 15 excerpts maximum per request. |
| Grounding | The prompt requires the model to answer only from retrieved context. |
| Latency and cost | Local embeddings avoid embedding API calls; Groq handles generation only. |
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
