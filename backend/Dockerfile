FROM python:3.14.10-alpine3.24 AS production

WORKDIR /api

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN addgroup -S appgroup && adduser -S -D -G appgroup appuser

COPY --chown=appuser:appgroup . .

ENV PYTHONDONTWRITEBYTECODE=1

USER appuser

CMD ["fastapi", "run", "src/main.py", "--host", "0.0.0.0", "--port", "8000"]