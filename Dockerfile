# Base Python Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PORT=5000

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend website files
COPY index.html dashboard.html connect.html analyze.html login.html runtime-test.html script.js style.css supabaseClient.js ./
COPY figures/ ./figures/

# Copy backend application and models
COPY backend/ ./backend/
COPY ml_model/ ./ml_model/

# Expose default port
EXPOSE 5000

# Run with Gunicorn WSGI server (1 worker + threads to stay lean in 512MB RAM)
CMD ["sh", "-c", "gunicorn --chdir backend app:app --bind 0.0.0.0:${PORT:-5000} --workers 1 --threads 4 --timeout 120"]
