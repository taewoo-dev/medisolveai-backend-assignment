FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libssl-dev pkg-config \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
        "asyncmy>=0.2.10" \
        "cryptography>=46.0.3" \
        "fastapi[standard]>=0.121.0" \
        "httpx>=0.28.1" \
        "pydantic-settings>=2.11.0" \
        "sqlalchemy[asyncio]>=2.0.44" \
    && apt-get purge -y build-essential pkg-config \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
