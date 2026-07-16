FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent ./agent
COPY api ./api
COPY governance ./governance
COPY knowledge ./knowledge
COPY observability ./observability
COPY harness ./harness
COPY ui ./ui

ENV PYTHONPATH=/app
ENV AGENT_MODE=auto
ENV AUDIT_LOG_PATH=/app/data/audit.jsonl

EXPOSE 8080
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
