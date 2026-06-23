FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Environment variables (set at runtime – do not hardcode)
ENV OPENAI_API_KEY=dummy
ENV OPENAI_BASE_URL=http://ollama:11434/v1
ENV OPENAI_MODEL=qwen3:0.6b

# Expose the API port
EXPOSE 8000

# Run the API server
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]