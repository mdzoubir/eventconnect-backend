#!/bin/bash
# vercel_build_script.sh
echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate --noinput
