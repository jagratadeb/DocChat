# DocChat - AI Document Q&A Assistant

Upload up to 5 PDF or text documents and ask questions across all of them at once.
Answers are grounded in retrieved excerpts using Retrieval-Augmented Generation (RAG),
with sources shown for every response.

Built entirely with free tools: LangChain, HuggingFace embeddings, FAISS, Groq, and
Streamlit. See the in-app Architecture page for a full technical explanation,
including how retrieval is optimized for accuracy across multiple documents without
increasing API cost.

## How it works (short version)

1. Each uploaded document is split into overlapping chunks, tagged with its filename.
2. Chunks are embedded locally and for free using a HuggingFace sentence-transformer model.
3. A separate FAISS index is built per document (not one merged index) - this is what
   prevents one document's content from crowding out another's in a multi-file session.
4. On each question, a fixed number of chunks is retrieved from every document
   independently, merged, and sent to the Groq API to generate the final answer.

## Project structure

```
ai-doc-qa-assistant/
├── app.py                       # Entry point: top navigation (Chat, Architecture)
├── app_pages/
│   ├── chat.py                  # Main chat UI
│   └── architecture.py          # Architecture / design-decisions page
├── styles.py                    # Shared dark theme CSS
├── rag_pipeline.py              # RAG logic: loading, chunking, embeddings, retrieval, generation
├── requirements.txt             # Python dependencies
├── runtime.txt                  # Pins Python version for Streamlit Cloud
├── .gitignore                   # Keeps .env and secrets out of version control
├── .env.example                  # Template for local API key config
├── .streamlit/
│   └── config.toml              # Dark theme configuration
├── DEPLOYMENT.md                 # Step-by-step free deployment guide
└── README.md
```

## 1. Get a free Groq API key

1. Go to https://console.groq.com
2. Sign up (free) and create an API key.
3. Keep it handy for the next step.

## 2. Run locally

```bash
cd ai-doc-qa-assistant

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\Activate.ps1

pip install -r requirements.txt

cp .env.example .env
# edit .env and paste your GROQ_API_KEY

streamlit run app.py
```

Open the URL Streamlit prints (usually http://localhost:8501).

No API key yet? Paste it into the sidebar's password field while the app is running -
it's held only in that session's memory and never written to disk.

## 3. Deploy for free

See `DEPLOYMENT.md` for the full step-by-step guide to deploying on Streamlit Community
Cloud, including how to set your API key as a secret so it never appears in your
repository.

## Security

- `.env` and `.streamlit/secrets.toml` are excluded by `.gitignore` and must never be
  committed.
- The API key is never printed, logged, or shown anywhere in the UI.
- Documents are processed in memory for the session only; nothing persists across
  sessions or users.

## Notes & limitations

- Up to 5 files per session; uploading more shows an error.
- Scanned/image-only PDFs are not OCR'd - text must be extractable.
- Processing a new batch of documents replaces the current session's index.
- Free Groq usage has rate limits; if you hit them, wait briefly and retry.
- `runtime.txt` pins Python to 3.11 for deployment. Some dependencies (notably Pillow,
  a transitive Streamlit dependency) don't yet ship prebuilt wheels for very new Python
  versions, which causes cloud builds to fail trying to compile from source. Don't
  remove this file when deploying.

## Possible next steps

- Persistent vector storage across sessions (e.g. Chroma with disk persistence)
- Multi-turn conversational memory
- OCR support for scanned PDFs
- Per-document relevance weighting instead of a fixed chunks-per-source count
