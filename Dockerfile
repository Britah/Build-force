# Dockerfile
FROM python:3.12-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies with virtual environment
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set PATH to use virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Create a startup script
RUN echo '#!/bin/bash\n\
set -e\n\
# Wait for database if needed\n\
echo "Applying database migrations..."\n\
python manage.py migrate\n\
echo "Collecting static files..."\n\
python manage.py collectstatic --noinput --clear\n\
echo "Starting Gunicorn..."\n\
exec gunicorn django-admin.wsgi:application --bind 0.0.0.0:$PORT\n\
' > /app/start.sh && chmod +x /app/start.sh

EXPOSE 8000

CMD ["/app/start.sh"]
