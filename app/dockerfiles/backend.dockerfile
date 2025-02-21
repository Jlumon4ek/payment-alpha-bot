FROM python:3.10-slim

WORKDIR /app

COPY requirements/requirements.txt /app/requirements/requirements.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    build-essential \
    libgmp-dev \
    curl \
    ffmpeg && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements/requirements.txt

COPY . /app

ENV PYTHONPATH=/app/src

CMD ["python", "src/main.py"]
