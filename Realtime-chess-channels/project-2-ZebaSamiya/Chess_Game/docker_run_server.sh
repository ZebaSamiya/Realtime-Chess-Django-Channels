#!/bin/bash

# Exit on error
set -e

# Collect static files (if you have any)
# Uncomment the next line if you use Django's static files
# python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate

# Start supervisord to manage processes
exec /usr/bin/supervisord -n