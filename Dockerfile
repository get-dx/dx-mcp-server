FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

RUN useradd -m -u 1000 mcp && \
    chown -R mcp:mcp /app

USER mcp

# Set environment variable placeholder (will be overridden at runtime)
ENV DB_URL=""
ENV DX_API_HOST="https://api.getdx.com"
ENV WEB_API_TOKEN=""

# Expose the entry point
ENTRYPOINT ["dx-mcp-server"]
CMD ["run"]
