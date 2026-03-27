FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ./pyproject.toml
COPY src/ ./src/

RUN pip install --no-cache-dir .

RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

CMD ["python", "-m", "src.simulator"]
