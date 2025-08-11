# Personal Finance Tracker (Django + DRF + JWT)

## Quick start
python -m venv .venv
. .venv/Scripts/activate   # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

## Demo data
python manage.py import_csv testuser sample.csv

## Auth
POST /api/token/ -> { access, refresh }
Use Authorization: Bearer <access>

## Docs
OpenAPI: /api/schema/
Swagger UI: /api/docs/
