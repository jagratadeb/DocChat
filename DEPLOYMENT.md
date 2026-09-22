# Deployment Guide - Streamlit Community Cloud (Free)

This guide deploys DocChat to a public URL at zero cost, with your Groq API key kept
out of source control.

## 1. Prepare the repository

Confirm these files are present and that `.gitignore` is in place before your first commit:

```
ai-doc-qa-assistant/
├── app.py
├── rag_pipeline.py
├── app_pages/
│   ├── chat.py
│   └── architecture.py
├── styles.py
├── requirements.txt
├── runtime.txt
├── .gitignore
├── .env.example
├── .streamlit/
│   └── config.toml
└── README.md
```

Do **not** commit a real `.env` file or `.streamlit/secrets.toml`. Both are already
excluded by `.gitignore`. Only `.env.example` (a template with no real key) should be
committed.

`runtime.txt` pins the Python version Streamlit Cloud builds with. Without it, the
platform may default to a very new Python version for which some dependencies (Pillow,
in particular) have no prebuilt wheel yet, causing the build to fail trying to compile
from source. Keep `runtime.txt` in the repo root as-is.

## 2. Push to GitHub

```bash
cd ai-doc-qa-assistant
git init
git add .
git status          # confirm .env is NOT listed here
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

If `git status` shows `.env` staged, stop and check your `.gitignore` before pushing -
rotate the key immediately if it was ever pushed.

## 3. Deploy on Streamlit Community Cloud

1. Go to https://share.streamlit.io and sign in with GitHub.
2. Click **New app**.
3. Select your repository, the `main` branch, and set the main file path to `app.py`.
4. Before clicking Deploy, open **Advanced settings**.

## 4. Add your Groq API key as a secret

Still in Advanced settings (or afterward via **App settings -> Secrets**), add:

```toml
GROQ_API_KEY = "your_real_groq_api_key_here"
```

This is the deployed equivalent of your local `.env` file. The app already reads keys
in this priority order: Streamlit secrets first, then environment variable - so no code
changes are needed between local and deployed environments.

## 5. Deploy

Click **Deploy**. The first build installs dependencies and can take a few minutes
(sentence-transformers, torch, and faiss-cpu are the largest). You'll receive a public
URL like:

```
https://your-app-name.streamlit.app
```

## 6. Redeploying after changes

Any `git push` to the connected branch automatically triggers a redeploy. No manual
steps are needed on Streamlit's side.

## Verifying secrets are not exposed

- Open your GitHub repo in a browser and confirm `.env` does not appear in the file list.
- In the deployed app, there is no key displayed anywhere in the UI - if you ever see one
  echoed in an error message, treat that key as compromised and regenerate it at
  console.groq.com immediately.
- Local secrets never leave your machine: `.env` is read only by `python-dotenv` at
  runtime and is excluded from git by `.gitignore`.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| "Missing Groq API key" on the deployed app | Secret not saved, or key name isn't exactly `GROQ_API_KEY` |
| Build fails on `pillow` with a zlib/compile error | `runtime.txt` missing or removed - Streamlit Cloud picked a Python version too new for Pillow's prebuilt wheels. Add/restore `runtime.txt` with `python-3.11` and redeploy. |
| Build fails on `faiss-cpu` | Version pin in `requirements.txt` should be `faiss-cpu>=1.9.0.post1`, not an exact old version |
| App works locally but not deployed | Check the "Manage app" logs in Streamlit Cloud for the actual stack trace |
