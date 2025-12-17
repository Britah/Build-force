#!/bin/bash
# build.sh
echo "Python version: $(python --version)"
echo "Starting build..."

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput --clear

echo "Build completed!"
