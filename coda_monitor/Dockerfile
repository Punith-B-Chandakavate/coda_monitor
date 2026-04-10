FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create logs directory
RUN mkdir -p logs staticfiles

# Collect static files and run migrations
RUN python manage.py collectstatic --noinput --settings=coda_monitor.settings_production || true
RUN python manage.py migrate --settings=coda_monitor.settings_production || true

EXPOSE 8000

# Run with gunicorn
CMD ["gunicorn", "coda_monitor.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--timeout", "120"]