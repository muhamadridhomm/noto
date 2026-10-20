# Noto — Local-First AI Notes

Noto is a web app for organizing notes and using an AI assistant to draft or tidy them. AI changes are staged for review before the user chooses whether to save them. This portfolio copy contains no personal note database; it creates a fresh local database when run.

## What it demonstrates

- Folders, pinned and unfiled notes, search, and note editing.
- A review step for AI-generated or tidied text before it is saved.
- Optional Gemini and Ollama providers configured by the user.
- A FastAPI backend with SQLite persistence and a Vue 3 frontend.

## Run locally

Requirements: Python 3.10+, Node.js, and npm.

1. In `backend`, create and activate a Python virtual environment, then install `requirements.txt`.
2. Copy `backend/.env.example` to `backend/.env` and fill only the provider settings you choose. Leave secrets out of Git.
3. Start the API from `backend` with `uvicorn app.main:app --reload --host 127.0.0.1 --port 8050`.
4. In another terminal, run `npm install` and `npm run dev` from `frontend`.
5. Open the local URL shown by Vite.

The database is created on the local machine and is excluded from Git. AI-provider availability and behavior depend on the user's own credentials or local Ollama installation.
