FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (this layer rarely changes, so gets cached)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip first (separate layer for caching)
RUN pip install --no-cache-dir --upgrade pip

# Copy requirements first for better Docker layer caching
COPY requirements_optimized.txt .

# Pre-install heavy dependencies in separate layers for better caching
# Install core LangChain dependencies first (heaviest)
RUN pip install --no-cache-dir \
    langchain==0.2.16 \
    langchain-core==0.2.40 \
    langchain-community==0.2.16

# Install OpenAI and related dependencies  
RUN pip install --no-cache-dir \
    openai==1.40.0 \
    langchain-openai==0.1.25

# Install CrewAI (separate layer as it's frequently updated)
RUN pip install --no-cache-dir crewai==0.41.1

# Install remaining lightweight dependencies
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    python-multipart==0.0.6 \
    pydantic==2.8.0 \
    requests==2.31.0 \
    python-dotenv==1.0.0 \
    httpx==0.25.2 \
    typing-extensions>=4.8.0 \
    sentence-transformers==2.7.0

# Clear pip cache to reduce image size
RUN pip cache purge

# Copy application code (this layer changes frequently, so goes last)
COPY . .

# Create necessary directories
RUN mkdir -p memory data government_cache

# Clean up Python bytecode to reduce image size
RUN find /usr/local/lib/python3.11/site-packages -name "*.pyc" -delete && \
    find /usr/local/lib/python3.11/site-packages -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

EXPOSE 8000

# Use environment variable for port flexibility
CMD ["sh", "-c", "uvicorn optimized_app:app --host 0.0.0.0 --port ${PORT:-8000}"]