FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including build tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PORT=8080

# Expose port for health checks
EXPOSE 8080

# Create startup script
RUN echo '#!/bin/bash\n\
# Start health check server in background\n\
python health_check.py &\n\
# Start the main agent\n\
python agent.py start\n\
' > /app/start.sh && chmod +x /app/start.sh

# Run both health check and agent
CMD ["/app/start.sh"]
