#!/bin/bash

echo "Installing dependencies..."
python -m pip install -r requirements.txt

echo "Waiting for database (10 seconds)..."
sleep 10

echo "Testing database connection..."
python << END
import psycopg2
import os
try:
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres.cqjczoluecxuaqxjwdkn",
        password=os.getenv('DB_PASSWORD'),
        host="aws-0-sa-east-1.pooler.supabase.com",
        port="6543",
        connect_timeout=30,
        sslmode='require'
    )
    print("Database connection successful!")
    conn.close()
except Exception as e:
    print("Database connection failed:", e)
    exit(1)
END

echo "Creating initial migrations..."
python manage.py makemigrations --noinput
python manage.py makemigrations sessions --noinput
python manage.py makemigrations admin --noinput
python manage.py makemigrations auth --noinput
python manage.py makemigrations contenttypes --noinput
python manage.py makemigrations portal_estudante --noinput

echo "Running migrations..."
python manage.py migrate --noinput
python manage.py migrate sessions --noinput
python manage.py migrate admin --noinput
python manage.py migrate auth --noinput
python manage.py migrate contenttypes --noinput
python manage.py migrate portal_estudante --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Creating static directory..."
mkdir -p static
cp -r staticfiles/* static/ 