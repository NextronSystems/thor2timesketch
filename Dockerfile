FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install OS dependencies (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirement files first (for layer caching)
COPY requirements.txt pyproject.toml ./

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Install the package
RUN pip install --no-cache-dir .

# Setup --user as an argument 
ARG UID=1000

# Create a non-root user
RUN useradd -ms /bin/bash -u $UID thor

# Change ownership of the app directory to the new user
RUN chown -R thor:thor /app

# Switch to the non-root user
USER thor

# Default command (can be overridden)
ENTRYPOINT ["thor2ts"]