FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md LICENSE ./

COPY src/ ./src/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

RUN pip install --no-cache-dir -e .

RUN useradd -m -u 1000 mcp && \
    chown -R mcp:mcp /app

USER mcp

# Set environment variable placeholder (will be overridden at runtime)
ENV DB_URL=""

# Expose the entry point
ENTRYPOINT ["dx-mcp-server"]
CMD ["run"]
