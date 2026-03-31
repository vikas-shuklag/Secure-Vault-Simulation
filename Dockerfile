FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for cryptography/psycopg2 compilation)
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run the API
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
