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

# Start the application
echo "Starting gunicorn..."
python -m gunicorn --config gunicorn.conf.py wsgi:application
