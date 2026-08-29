FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN useradd --create-home --uid 1000 display

COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir .

COPY data/riddles.json /data/riddles.json
RUN mkdir -p /data/cache && chown -R display:display /data

USER display

ENV CACHE_DIR=/data/cache \
    RIDDLES_PATH=/data/riddles.json \
    PORT=8080

EXPOSE 8080
VOLUME /data

HEALTHCHECK --interval=60s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import os,urllib.request;urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"PORT\"]}/healthz')"

CMD ["sh", "-c", "uvicorn wall_tidbits.app:app --host 0.0.0.0 --port ${PORT}"]
