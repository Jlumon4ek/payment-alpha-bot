FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    build-essential \
    libgmp-dev \
    curl && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements/requirements.txt

ENV PYTHONPATH=/app

CMD ["python", "main.py"]
