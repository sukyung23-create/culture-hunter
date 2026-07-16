# Use an official lightweight Python image
FROM python:3.11-slim

# Set environment variables for smooth, buffered output in cloud environments
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set working directory inside container
WORKDIR /app

# Install system dependencies (build-essential for fast feedparser parsing)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies first for efficient Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Pre-seed/rebuild the high-integrity SQLite events database inside the image during build
RUN python import_csv.py

# Expose the designated web server port
EXPOSE 8000

# Command to start the application with Uvicorn in production mode
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT}"]
