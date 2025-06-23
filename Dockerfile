FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install OS dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirement files first (for layer caching)
COPY requirements.txt requirements-dev.txt pyproject.toml ./

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -r requirements-dev.txt

# Copy source code
COPY src/ ./src/
COPY mypy.ini ./
COPY LICENSE README.md ./

# Optional: Set env vars
ENV PYTHONPATH=/app/src

# Default command (can be overridden)
ENTRYPOINT ["python", "-m", "thor2timesketch"]