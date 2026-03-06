FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN useradd -m -u 10001 appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY worker ./worker
COPY app ./app

RUN chown -R appuser:appuser /app
USER appuser

CMD ["celery", "-A", "worker.celery_app:celery_app", "worker", "--loglevel=INFO"]
