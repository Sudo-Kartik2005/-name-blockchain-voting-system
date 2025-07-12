#!/bin/bash
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Installing gunicorn explicitly..."
pip install gunicorn==21.2.0

echo "Verifying gunicorn installation..."
which gunicorn
gunicorn --version

echo "Build completed successfully!" 