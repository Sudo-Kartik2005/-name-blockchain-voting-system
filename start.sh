#!/bin/bash

# Startup script for Render deployment
echo "Starting blockchain voting system..."

# Check if gunicorn is installed
if ! python -c "import gunicorn" 2>/dev/null; then
    echo "Gunicorn not found, installing..."
    pip install gunicorn
fi

# Check if requirements are installed
if ! python -c "import flask" 2>/dev/null; then
    echo "Installing requirements..."
    pip install -r requirements.txt
fi

# Get the port from environment variable (Render sets this)
PORT=${PORT:-8000}
echo "Starting on port: $PORT"

# Start the application with explicit configuration
echo "Starting gunicorn..."
python -m gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --timeout 30 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    wsgi:application
