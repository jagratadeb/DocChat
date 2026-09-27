# DocChat Security and Privacy

This document explains how DocChat handles files, questions, generated answers, API keys, and session data. It describes the behavior implemented in this repository. It is not legal advice or a substitute for the privacy terms of the service used to host DocChat or the third-party providers used by the app.

## Quick summary

- Uploaded files are processed for the current Streamlit session and are not intentionally written to a permanent application database.
- Files are briefly written to temporary paths so PDF and text loaders can read them. The temporary path is removed after loading, including when loading fails.
- Text extraction, chunking, embeddings, and FAISS retrieval run locally in the Streamlit process.
- The user's question, selected retrieved excerpts, and source filenames are sent to Groq to generate an answer.
- The embedding model runs locally. Uploaded document content is not sent to Hugging Face for embedding requests.
- Session indexes, document names, chat history, and generated answers are held in Streamlit session state and process memory.
- The app has no user accounts, document permissions, or application-level encryption controls.
- Do not upload confidential, regulated, or sensitive information unless you have assessed the hosting and third-party provider terms and accept the associated risks.

## What data DocChat handles

During a session, the app may handle:

- Uploaded PDF, TXT, and Markdown file contents.
- Original uploaded filenames.
- Extracted document text and metadata, including PDF page information when available.
- Text chunks created from the uploaded files.
- The questions entered in the chat box.
- Retrieved excerpts used to answer each question.
- Generated answers and displayed source excerpts.
- Session counters such as indexed file count and chunk count.
- A Groq API key supplied through deployment secrets, an environment variable, or the password-masked key field.

The app does not intentionally collect a name, email address, account profile, or payment information. Hosting infrastructure, browser telemetry, reverse proxies, and third-party services may have their own logs and data practices outside this application code.

## What happens when a file is uploaded

1. Streamlit receives the uploaded file in the active browser session.
2. DocChat writes the file bytes to a temporary file so the appropriate LangChain loader can read the file.
3. PDF, TXT, or Markdown content is extracted. Scanned or image-only PDFs are not OCR'd by this version.
4. The temporary file is deleted in a cleanup block after loading.
5. Extracted documents are tagged with the original filename and split into overlapping text chunks.
6. The chunks are embedded with the local `all-MiniLM-L6-v2` model.
7. A separate in-memory FAISS index is built for each uploaded source file.

The application does not intentionally upload the original file to Groq. However, excerpts derived from the file may be sent to Groq when the user asks a question.

## What is sent to Groq

For each question, DocChat retrieves up to three excerpts per indexed file and sends the following to Groq's configured chat model:

- The user's question.
- The retrieved text excerpts.
- Labels containing the source filename and, where available, page information.
- The application prompt instructing the model to answer only from the supplied context.

With the current limits, a maximum of five files and three excerpts per file can contribute to one request, for a maximum of 15 retrieved excerpts. This limits request size but does not prevent sensitive information contained in those excerpts from being transmitted to Groq.

Groq is a separate service. Its retention, abuse monitoring, training, regional processing, and deletion practices are governed by the applicable Groq terms and privacy documentation, not by this repository. Review those terms before using DocChat with sensitive documents.

## What stays local to the app process

The following are handled locally by the running Streamlit process:

- File parsing and text extraction.
- Text chunking.
- Embedding generation after the embedding model is available locally.
- FAISS index construction and similarity search.
- Session document names, indexes, chat history, and generated-answer display state.

The embedding model is cached at process level for reuse. That cache is model data, not a permanent copy of a user's uploaded documents. The app does not create a persistent document store or save FAISS indexes to a repository directory.

## Retention and deletion

Within the app:

- Temporary parsing files are removed after loading.
- Active indexes and chat state remain available for the Streamlit session so follow-up questions can work.
- Processing a new batch replaces the active indexes and chat history.
- The **Clear session** control removes the active vectorstores, language model reference, document names, chunk count, chat history, and processing status from session state.
- Session state is not designed as permanent storage and is normally discarded when the session ends or the hosting process is restarted.

This does not guarantee deletion from browser memory, operating-system caches, hosting logs, crash reports, provider logs, backups, or Groq systems. The hosting platform and external providers may retain operational data according to their own policies.

## API key protection

DocChat reads the Groq key in this order:

1. Streamlit secrets, for deployed environments.
2. The `GROQ_API_KEY` environment variable, commonly loaded from a local `.env` file.
3. The password-masked key input in the chat sidebar when no configured key is available.

The application does not intentionally display, log, or write the key. Operators must still protect the deployment configuration and machine running the app.

Never commit `.env`, `.streamlit/secrets.toml`, or any file containing a real key. If a key is exposed in source control, logs, screenshots, browser history, or an error report, revoke and rotate it immediately through Groq.

## Hosting and transport considerations

The security of a DocChat deployment also depends on its hosting environment:

- A local Streamlit server may be reachable by other devices on the configured network. Use appropriate network controls and do not expose it publicly without protection.
- A public Streamlit Community Cloud deployment is accessible at its public URL unless access controls are configured through the platform or an additional layer.
- HTTPS, network isolation, platform logs, backups, and infrastructure access are controlled by the hosting platform and deployment configuration.
- This application does not implement login, role-based access control, tenant isolation, audit logging, or per-user document authorization.
- Do not assume that a public URL provides private document storage or private access by itself.

Use a trusted deployment, keep dependencies and the hosting platform updated, restrict access where possible, and configure secrets through the host's secret manager rather than source files.

## Security limitations

The current application does not provide:

- End-to-end encryption controlled by the application.
- Client-side encryption before upload.
- Persistent encrypted document storage.
- User authentication or account-level authorization.
- Per-document access policies.
- Malware scanning or content disarm-and-reconstruct processing.
- OCR for image-only PDFs.
- A guaranteed deletion workflow for third-party or platform logs.
- A formal compliance certification or guarantee for regulated data.

Uploaded files are parsed by third-party libraries. Treat files from untrusted sources carefully and keep the runtime dependencies patched.

## Recommended user practices

- Upload only the minimum documents needed for the question.
- Remove passwords, secrets, access tokens, personal identifiers, and unrelated confidential data before uploading.
- Prefer redacted or synthetic documents when testing the app.
- Confirm that your organization permits sending the relevant excerpts to Groq.
- Use a deployment with HTTPS and access control for anything beyond local experimentation.
- Clear the session after finishing, close the browser tab, and avoid sharing screenshots or exported logs containing document content.
- Rotate any credential that may have appeared in a document, prompt, answer, log, or screenshot.

## Reporting a security issue

Do not publish credentials, private documents, or exploit details in a public issue. Contact the application maintainer through the repository's private security or contact channel, and include a minimal reproducible description without sensitive data.

## Scope and changes

This document reflects the current repository behavior. Reassess it whenever the app adds persistent storage, user accounts, analytics, file previews, background jobs, new model providers, or a different deployment platform.
