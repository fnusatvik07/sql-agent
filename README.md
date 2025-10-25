# 🚀 SQLAgent — FastAPI + LangChain + Render Deployment

A production-ready backend built with **FastAPI**, **LangChain**, and **LangGraph**, using **uv** for dependency management and deployed automatically to **Render** via **GitHub Actions**.

---

## 🧩 Project Overview

**SQLAgent** is an intelligent FastAPI service that connects to a SQL database and uses an LLM to answer natural-language queries.

It includes:

* ⚙️  **FastAPI** backend for REST endpoints (`/chat`, `/health`)
* 🧠  **LangChain + LangGraph** for SQL reasoning
* 🗃️  **SQLite (Chinook.db)** as a demo database
* ⚡  **uv** package manager for blazing-fast builds
* ☁️  **Render** for deployment
* 🔁  **GitHub Actions** CI/CD for automatic deployment

---

## 🛠️ Local Development

### 1️⃣  Create and activate virtual environment

```bash
uv venv
source .venv/bin/activate
```

### 2️⃣  Install dependencies

```bash
uv sync
```

### 3️⃣  Run the app locally

```bash
uv run uvicorn main:app --reload
```

Then open:
👉 [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🐳 Docker Support

To build and run locally in Docker:

```bash
docker build -t sqlagent:latest .
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  sqlagent:latest
```

Sample `.env`:

```
OPENAI_API_KEY=sk-your-api-key
PORT=8000
```

---

## ☁️ Deploying on Render

### Step 1: Create a Render Web Service

1. Go to [Render Dashboard](https://dashboard.render.com).
2. Create a new **Web Service** from your GitHub repo.
3. Copy the **Service ID** from your URL (e.g. `srv-d3uhdh0dl3ps73f5i7c0`).
4. Generate a **Render API Key** from your account settings.

### Step 2: Add GitHub Secrets

In your GitHub repo → **Settings → Secrets → Actions**, add:

| Name                | Value                                                    |
| ------------------- | -------------------------------------------------------- |
| `RENDER_API_KEY`    | your Render API key                                      |
| `RENDER_SERVICE_ID` | your Render service ID (e.g. `srv-d3uhdh0dl3ps73f5i7c0`) |

### Step 3: GitHub Actions Workflow

GitHub Actions automatically triggers deployment whenever you push to `main`.

File: `.github/workflows/deploy.yml`

```yaml
name: Deploy to Render

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Trigger deployment on Render
        env:
          RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
          RENDER_SERVICE_ID: ${{ secrets.RENDER_SERVICE_ID }}
        run: |
          echo "🚀 Triggering deployment on Render..."
          curl -X POST \
            -H "Accept: application/json" \
            -H "Authorization: Bearer $RENDER_API_KEY" \
            -d '' \
            "https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploys"
```

Once pushed, check the **Actions** tab on GitHub and the **Render Deployments** page — your backend should redeploy automatically 🎉

---

## 🧠 Endpoints

| Endpoint      | Description                                                             |
| ------------- | ----------------------------------------------------------------------- |
| `GET /health` | Health check for DB and API                                             |
| `POST /chat`  | Accepts `{ "question": "..." }` and returns an LLM-generated SQL answer |

Example request:

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"question": "How many customers are from Brazil?"}'
```

Response:

```json
{
  "question": "How many customers are from Brazil?",
  "answer": "There are 5 customers from Brazil.",
  "execution_time_sec": 3.9
}
```

---

## 🧰 Tech Stack

| Component          | Technology            |
| ------------------ | --------------------- |
| Framework          | FastAPI               |
| LLM Layer          | LangChain + LangGraph |
| Database           | SQLite (Chinook.db)   |
| Dependency Manager | uv                    |
| Deployment         | Render                |
| CI/CD              | GitHub Actions        |

---

## ⚡ Quick Commands

| Task                  | Command                                                                                                                         |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Run locally           | `uv run uvicorn main:app --reload`                                                                                              |
| Build Docker image    | `docker build -t sqlagent:latest .`                                                                                             |
| Run Docker container  | `docker run -d -p 8000:8000 --env-file .env sqlagent:latest`                                                                    |
| Trigger manual deploy | `curl -X POST -H "Authorization: Bearer $RENDER_API_KEY" -d '' "https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploys"` |
