#!/bin/sh

# Run migrations
python manage.py migrate --noinput

# Create test users
python manage.py create_test_users

# Start server
exec python manage.py runserver 0.0.0.0:8000
