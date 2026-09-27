# DocChat

DocChat is a Streamlit application that lets users upload a small set of documents,
ask questions in plain language, and receive answers based on the uploaded content.
Answers include the file and page information used to produce them when that
information is available.

## Version

Current release: **v1.2.0**

## What DocChat includes

- A landing page with a direct path into the document chat workflow.
- A Chat page for uploading files and asking questions.
- Support for PDF, TXT, and Markdown files.
- A maximum of 5 files per visit.
- File-by-file search so every uploaded file can contribute to an answer.
- Up to 3 relevant text parts selected from each file for a question.
- A maximum of 15 selected text parts for one question when 5 files are loaded.
- File and page references displayed with answers when available.
- An Architecture page explaining the technical pipeline and its design decisions.
- A plain-language Privacy & Security page explaining data handling and Groq usage.
- Responsive styling for desktop and mobile screens.

## User workflow

1. Open the Home page.
2. Select **Start Chatting**.
3. Choose up to 5 PDF, TXT, or Markdown files.
4. Select **Read my files**.
5. Ask a question in the chat box.
6. Open **Where this answer came from** to inspect the file parts used for the answer.

The **Remove files and answers** control in the Chat sidebar clears the active files,
search data, and chat history for the current visit.

## How it works

### 1. File reading

Uploaded files are written to a temporary path so the appropriate PDF or text loader
can read them. The temporary path is removed after loading. Scanned or image-only PDFs
are not read because this version does not include OCR.

### 2. Text preparation

Extracted text is split into overlapping sections of 1,000 characters with a
250-character overlap. Each section keeps the original filename and PDF page metadata
when available.

### 3. Local search

The `all-MiniLM-L6-v2` embedding model runs locally in the application process. A
separate FAISS search index is created for each uploaded file. For every question,
DocChat searches each file independently and selects up to 3 relevant sections per
file.

### 4. Answer generation

The selected sections and the user's question are sent to Groq's
`openai/gpt-oss-120b` chat model. The prompt instructs the model to answer only from
the supplied sections and to say when the files do not contain the answer.

This approach gives every uploaded file an opportunity to contribute while keeping
the amount of text sent for one question predictable.

## Pages and navigation

The top navigation contains four pages:

- **Home**: Introduction and entry point to the app.
- **Chat**: File upload, file preparation, questions, answers, and answer references.
- **Architecture**: Technical details, pipeline diagram, limits, and failure behavior.
- **Privacy & Security**: Plain-language information about file handling, Groq, and
  deployment risks.

The Architecture page is intentionally technical. The other pages use simpler,
non-technical language for general users.

## Privacy and security

Read [SECURITY_AND_PRIVACY.md](SECURITY_AND_PRIVACY.md) for the complete explanation.
The important points are:

- Files are handled for the active Streamlit visit and are not intentionally saved in
  a permanent document database by this application.
- Search data and chat history remain in the active application session.
- The original file is not intentionally sent to Groq as one complete upload.
- For each question, Groq receives the question, selected text parts, and file/page
  labels needed to create the answer.
- Groq and the hosting platform have their own retention, logging, and security rules.
- The application does not provide sign-in, user accounts, per-user permissions, or
  application-controlled end-to-end encryption.
- Do not upload confidential or regulated information unless the hosting and provider
  terms have been reviewed and the risk is acceptable.

## Requirements

- Python 3.11
- A Groq API key
- Enough memory for the local embedding model and FAISS indexes
- Internet access for Groq requests and the first embedding-model download

The Python dependencies are pinned in [requirements.txt](requirements.txt). The
deployment runtime is specified in [runtime.txt](runtime.txt).

## Run locally

### 1. Create a virtual environment

PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
python -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the Groq key

For a PowerShell session:

```powershell
$env:GROQ_API_KEY = "your_groq_api_key"
```

Or create a local `.env` file in the project root:

```dotenv
GROQ_API_KEY=your_groq_api_key
DOCCHAT_LINKEDIN_URL=https://www.linkedin.com/in/your-profile
DOCCHAT_GITHUB_URL=https://github.com/your-username
DOCCHAT_X_URL=https://x.com/your-username
DOCCHAT_BLUESKY_URL=https://bsky.app/profile/your-handle
```

The social URLs are optional. They are shown in the footer when configured.

Never commit `.env` or a file containing a real key. Both local secrets and
`.streamlit/secrets.toml` are excluded through `.gitignore`.

### 4. Start the app

```bash
streamlit run app.py
```

Open the local URL printed by Streamlit, normally:

```text
http://localhost:8501
```

## Deploy on Streamlit Community Cloud

The full deployment guide is in [DEPLOYMENTS.md](DEPLOYMENTS.md). The short version:

1. Push the repository to GitHub without `.env` or `.streamlit/secrets.toml`.
2. Create a new Streamlit Community Cloud app.
3. Select the repository and branch.
4. Set `app.py` as the main file.
5. Add the Groq key in the platform's Secrets settings:

   ```toml
   GROQ_API_KEY = "your_real_groq_api_key_here"
   ```

6. Deploy the app.

The first deployment can take several minutes because the local embedding model and
FAISS-related dependencies are larger than the typical Streamlit package.

## Configuration notes

- `MAX_FILES` is set to 5 in [rag_pipeline.py](rag_pipeline.py).
- `CHUNKS_PER_SOURCE` is set to 3 in [rag_pipeline.py](rag_pipeline.py).
- Text chunks use a 1,000-character size and 250-character overlap.
- The configured Groq model is `openai/gpt-oss-120b`.
- The embedding model is `all-MiniLM-L6-v2`.
- Streamlit's own upload-size setting may also limit individual file size. Configure
  it in `.streamlit/config.toml` if the deployment needs a different limit.

## Project structure

```text
ai-doc-qa-assistant/
├── app.py                              # Streamlit entry point and page navigation
├── app_pages/
│   ├── home.py                         # Landing page
│   ├── chat.py                         # Upload and document chat workflow
│   ├── architecture.py                 # Technical architecture page
│   └── security.py                     # Plain-language security page
├── rag_pipeline.py                     # Loading, search, and answer generation
├── styles.py                           # Shared CSS and header/footer styling
├── SECURITY_AND_PRIVACY.md             # Detailed data-handling documentation
├── DEPLOYMENTS.md                      # Streamlit Community Cloud guide
├── requirements.txt                    # Python dependencies
├── runtime.txt                         # Deployment Python version
├── .streamlit/config.toml              # Streamlit configuration
├── docchat_architecture_detailed.png   # Architecture diagram
└── README.md                           # Project documentation
```

## Troubleshooting

### The app says a Groq key is missing

Set `GROQ_API_KEY` in the environment, `.env`, or Streamlit secrets. The key name must
be exactly `GROQ_API_KEY`.

### A file cannot be read

Confirm that it is a PDF, TXT, or Markdown file and that the PDF contains selectable
text. Scanned PDFs require OCR, which is not included in this version.

### The first question is slow

The first file-reading request may download and load the local embedding model. Later
questions in the same running process can reuse that model.

### The deployment build fails

Confirm that `runtime.txt` is present and that the deployment is using Python 3.11.
See [DEPLOYMENTS.md](DEPLOYMENTS.md) for platform-specific troubleshooting.

### Answers are not found in the files

Ask a more specific question using terms that appear in the files. DocChat is designed
to avoid guessing and may say that the answer is not present when the selected text
does not contain enough information.

## Development checks

Compile the main Python modules before committing:

```bash
python -m py_compile app.py app_pages/home.py app_pages/chat.py app_pages/architecture.py app_pages/security.py rag_pipeline.py styles.py
```

## Release history

### v1.2.0

- Added the landing page and guided Home-to-Chat flow.
- Added the Privacy & Security navigation page and documentation.
- Expanded and repaired the Architecture page and diagram layout.
- Improved responsive styling and upload-limit messaging.
- Replaced technical user-facing labels with clearer plain language.

## License and responsibility

Review the repository's licensing and deployment requirements before distributing the
application. DocChat is provided with the limitations described in
[SECURITY_AND_PRIVACY.md](SECURITY_AND_PRIVACY.md); operators should assess their own
hosting, provider, and data-protection requirements before production use.