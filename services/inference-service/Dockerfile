FROM python:3.11-slim AS base

# System deps for OpenCV and grpc
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project definition and source together
COPY pyproject.toml ./pyproject.toml
COPY src/ ./src/

# Install runtime deps
RUN pip install --no-cache-dir .

# Non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

EXPOSE 8001
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "2"]
