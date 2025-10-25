# ─────────────────────────────
# 1️⃣ Base image with Python
# ─────────────────────────────
FROM python:3.12-slim

# ─────────────────────────────
# 2️⃣ Environment variables
# ─────────────────────────────
ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    APP_HOME=/app \
    PORT=8000

WORKDIR $APP_HOME

# ─────────────────────────────
# 3️⃣ Install system dependencies + uv
# ─────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends curl sqlite3 && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    rm -rf /var/lib/apt/lists/*

# Ensure uv is in PATH (added by install script)
ENV PATH="/root/.cargo/bin:/root/.local/bin:$PATH"

# ─────────────────────────────
# 4️⃣ Copy your project
# ─────────────────────────────
COPY . .

# ─────────────────────────────
# 5️⃣ Sync all dependencies via pyproject.toml
# ─────────────────────────────
RUN uv sync --frozen --python 3.12

# ─────────────────────────────
# 6️⃣ Expose and launch FastAPI app
# ─────────────────────────────
EXPOSE ${PORT}

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
