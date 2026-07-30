FROM python:3.11-slim

WORKDIR /app

# System dependencies for Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo-dev libwebp-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE $PORT

CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
