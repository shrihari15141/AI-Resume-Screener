# PythonAnywhere Deployment

This project deploys as one Flask web application that serves the React/Vite production build and handles all `/api/*` routes from the same PythonAnywhere domain.

Production shape:

- `https://YOURUSERNAME.pythonanywhere.com/` serves the React app from `backend/static/index.html`
- `https://YOURUSERNAME.pythonanywhere.com/assets/*` serves Vite build assets
- `https://YOURUSERNAME.pythonanywhere.com/api/*` serves Flask API routes
- SQLite defaults to `backend/instance/database.sqlite`
- Resume uploads default to `backend/uploads/`

## Requirements

- Python 3.10
- Node.js/npm for building the frontend during deployment
- No login credentials are required by the frontend; the app opens directly for recruiter use

## 1. Clone The Repository

In a PythonAnywhere Bash console:

```bash
cd ~
git clone https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY.git AI-Resume-Screener
cd ~/AI-Resume-Screener
```

## 2. Create A Python 3.10 Virtualenv

```bash
python3.10 -m venv ~/.virtualenvs/resumescreener
source ~/.virtualenvs/resumescreener/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Create `.env`

Copy the example and fill in only values you actually use:

```bash
cp .env.example .env
nano .env
```

Recommended production values:

```bash
FLASK_ENV=production
SECRET_KEY=replace-with-a-long-random-value
JWT_SECRET_KEY=replace-with-a-different-long-random-value
DATABASE_URL=
UPLOAD_FOLDER=uploads
MAX_UPLOAD_MB=20
MAX_BATCH_UPLOAD_MB=1024
CORS_ORIGINS=

LLM_API_KEY=
LLM_MODEL=
LLM_API_URL=

VITE_API_URL=/api
```

Do not put real secrets in GitHub. Anything beginning with `VITE_` is exposed to the browser, so never place private API keys in a `VITE_` variable.

## 4. Build The React Frontend

```bash
cd ~/AI-Resume-Screener/frontend
npm install
npm run build
test -f ../backend/static/index.html
```

The Vite build output must exist at:

```text
backend/static/index.html
backend/static/assets/
```

## 5. Configure The PythonAnywhere Web App

In the PythonAnywhere Web tab:

- Add a new web app
- Choose manual configuration
- Select Python 3.10
- Set the virtualenv to:

```text
/home/YOURUSERNAME/.virtualenvs/resumescreener
```

- Set the source code / working directory to:

```text
/home/YOURUSERNAME/AI-Resume-Screener
```

## 6. Configure WSGI

Edit the PythonAnywhere WSGI file and use this structure:

```python
import os
import sys

project_path = "/home/YOURUSERNAME/AI-Resume-Screener"
backend_path = os.path.join(project_path, "backend")

if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

os.chdir(project_path)

from app import app as application
```

Replace `YOURUSERNAME` with your PythonAnywhere username. Do not call `app.run()` from the WSGI file.

## 7. Reload And Test

Reload the web app from the PythonAnywhere Web tab, then test:

```bash
curl https://YOURUSERNAME.pythonanywhere.com/api/health
```

Expected response:

```json
{"status":"ok"}
```

Open:

```text
https://YOURUSERNAME.pythonanywhere.com/
```

The React app should load from the same URL, and API requests should go to `/api/*` on that domain.

## Local Development

Backend:

```bash
cd backend
python app.py
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` to `http://localhost:5000`. If you prefer direct API calls, create a frontend-local env file and set:

```bash
VITE_API_URL=http://localhost:5000/api
```

Production-style local test:

```bash
cd frontend
npm run build
cd ../backend
python app.py
```

Then open:

```text
http://localhost:5000/
```

## Notes And Limits

- PythonAnywhere does not use the `Procfile`; it imports the Flask app through WSGI.
- The existing `Procfile` is only for platforms that run `gunicorn`.
- `backend/static/`, `backend/uploads/`, `backend/instance/`, `.env`, SQLite databases, `node_modules/`, and caches should not be committed.
- Very large resume batches may be affected by PythonAnywhere CPU, memory, disk, and request/runtime limits.
- The current batch status store is in memory, so queued status can be lost if the web app reloads while a batch is running.
- Heavy optional ML packages such as `sentence-transformers` may exceed lower-tier PythonAnywhere resource limits; the app has deterministic fallback behavior if semantic model loading fails.
