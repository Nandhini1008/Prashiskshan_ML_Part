# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy chatbot application code
COPY . .

# Create data directory if it doesn't exist
RUN mkdir -p data/companies data/faqs data/college_docs

# Expose the chatbot service port
EXPOSE 5001

# Set environment variables with defaults
ENV CHATBOT_SERVICE_PORT=5001
ENV CHATBOT_SERVICE_HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

# Health check (using curl or wget if available, otherwise Python)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5001/health')" || exit 1

# Run the chatbot service
CMD ["python", "chatbot_service.py"]

