"""
app_pages/architecture.py

Explains how the system works: the retrieval pipeline, what the Groq API
is used for, and how API calls are kept cheap without hurting answer
quality across multiple documents.
"""

from pathlib import Path

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

architecture_image = Path(__file__).resolve().parents[1] / "docchat_architecture_detailed.png"
_, diagram_column, _ = st.columns([1.5, 2, 1.5])
with diagram_column:
  st.image(
    str(architecture_image),
    caption="From uploaded files to a sourced answer",
    use_column_width=True,
  )

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

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("End-to-end request flow")
st.markdown("""
<div class="architecture-flow">
<div><b>1. Upload</b><span>Up to five PDF, TXT, or Markdown files enter the active Streamlit session.</span></div>
<div><b>2. Extract</b><span>PDF and text loaders turn each file into readable LangChain documents.</span></div>
<div><b>3. Prepare</b><span>Text is split into 1,000-character chunks with 250 characters of overlap.</span></div>
<div><b>4. Search</b><span>Each file gets its own FAISS index, and three nearby chunks are found per file.</span></div>
<div><b>5. Generate</b><span>The question and selected chunks are sent to Groq's chat model.</span></div>
<div><b>6. Present</b><span>The answer is shown with the file names and page numbers used as sources.</span></div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

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
st.subheader("Limits and failure behavior")
st.markdown("""
| Situation | What the app does |
|---|---|
| More than five files are selected | Stops before reading them and asks the user to select five or fewer. |
| An unsupported file type is selected | Rejects the file and reports the supported PDF, TXT, and Markdown types. |
| A PDF has no readable text | Reports that the file could not be read; scanned PDFs are not OCR'd. |
| No text chunks are produced | Stops indexing and reports that there is no searchable text. |
| No Groq key is available | Asks for the key before creating answers. |
| The answer is not in the selected text | Instructs the model to say that the files do not contain the answer. |
| A question is asked before files are ready | The chat box is not shown until files are successfully prepared. |
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
st.subheader("What leaves the app")
st.markdown("""
File reading, text splitting, local embeddings, and FAISS searching happen in the
running app process. For each question, only the question, the selected text parts,
and their file and page labels are sent to Groq for answer generation. The complete
original file is not intentionally sent as one request.
""")
st.markdown('</div>', unsafe_allow_html=True)

inject_app_footer()

