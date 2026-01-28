#!/usr/bin/env bash
# Exit on error
set -o errexit

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Seed sample data (since SQLite is ephemeral on Render)
echo "Seeding sample data..."
python manage.py seed_sample_data --clear

# Start the application
echo "Starting Gunicorn..."
gunicorn groundwater.wsgi:application
