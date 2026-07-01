FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for MySQL client and build tools
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy python project configuration
COPY pyproject.toml .

# Install python dependencies
RUN pip install --no-cache-dir -e .

# Copy application code
COPY . .

# Make entrypoint executable
RUN chmod +x /app/start-backend.sh

EXPOSE 8000

CMD ["/app/start-backend.sh"]
