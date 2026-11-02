# Noto — Local-First Notes & Planning Workspace

Noto brings everyday notes and lightweight task planning into one local workspace. Its AI assistant can draft or tidy text, but suggestions stay in a review step until the user chooses to apply them.

## What it demonstrates

- Organize notes in folders, pin important notes, keep unfiled notes, and search across content.
- Capture checklists and tasks with groups, status, priority, and due dates; track milestones and review task history.
- Start from reusable note and task templates, then export planning data as Excel or HTML.
- Use a FastAPI backend with SQLite persistence and a Vue 3 interface.
- Configure Gemini with a key supplied by the user, or use a local Ollama installation.
- Keep AI-generated changes staged for human review before saving.

This public edition contains application code and generic templates only. Personal note databases, employer-specific examples, credentials, and generated user data are excluded. The Firebase sync experiment is not included in this edition.

## Run locally

Requirements: Python 3.10+, Node.js, and npm.

1. From the project root, run `./start.sh --dev`.
2. The script creates the backend virtual environment and installs dependencies if needed, then starts the API and Vite development server.
3. Open the local URL printed by Vite; the FastAPI docs are available at `http://127.0.0.1:8050/docs`.
4. To use Gemini, add `GEMINI_API_KEY` to `backend/.env`. For local generation, install Ollama and choose a model available on your machine.

Local note and planning data is stored in SQLite and excluded from Git. AI provider availability depends on the user's own API key or local Ollama setup.
