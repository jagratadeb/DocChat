# Deployment Guide - Streamlit Community Cloud (Free)

This guide deploys DocChat to a public URL at zero cost, with your Groq API key kept
out of source control.

## 1. Prepare the repository

Confirm these files are present and that `.gitignore` is in place before your first commit:

```
ai-doc-qa-assistant/
├── app.py
├── rag_pipeline.py
├── pages/
│   └── 1_Architecture.py
├── requirements.txt
├── .gitignore
├── .env.example
├── .streamlit/
│   └── config.toml
└── README.md
```

Do **not** commit a real `.env` file or `.streamlit/secrets.toml`. Both are already
excluded by `.gitignore`. Only `.env.example` (a template with no real key) should be
committed.

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
(sentence-transformers and faiss-cpu are the largest). You'll receive a public URL like:

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
| Build fails on `faiss-cpu` | Pin version per `requirements.txt`; Streamlit Cloud runs Linux, so Windows-specific wheel issues do not apply there |
| App works locally but not deployed | Check the "Manage app" logs in Streamlit Cloud for the actual stack trace |
