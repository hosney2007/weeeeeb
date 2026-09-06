# Abdelfatah Academy Web Platform

Flask educational platform with student authentication, recorded courses, bookings, school portal, assignments, admin management, and MySQL (Hostinger) support.

## Setup
1. Create a Python virtual environment.
2. Install dependencies: `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and set production secrets.
4. For production, use the MySQL database created in Hostinger's hPanel (Databases -> MySQL Databases) — see `.env.example` for the connection string format. Don't use SQLite in production.
5. Run locally with `python file.py`, or with Gunicorn using `gunicorn file:app`.

## Deploying on Hostinger
1. In hPanel, go to **Advanced -> Setup Python App** and create a new app pointing at this project's folder.
   - Application startup file: `passenger_wsgi.py`
   - Application Entry point: `application`
2. Create a MySQL database under **Databases -> MySQL Databases**, and put its connection string in `DATABASE_URL` (format in `.env.example`).
3. Set all the environment variables from `.env.example` in hPanel's "Environment variables" section for the Python app.
4. Install dependencies from `requirements.txt` using the "Run pip install" button in hPanel (or via SSH: `pip install -r requirements.txt`).
5. Restart the app from hPanel after any code or dependency change.

Uploaded files (payment screenshots, course sheets, lesson thumbnails, etc.) are stored under `static/uploads/` by default when Supabase isn't configured — unlike Vercel, Hostinger's storage is persistent, so this works fine without any extra setup.

## Important environment variables
- `SECRET_KEY`: stable random secret in production.
- `DATABASE_URL`: MySQL connection string in production (`mysql+pymysql://user:password@host/dbname`).
- `MAIL_USERNAME` / `MAIL_PASSWORD`: SMTP credentials for verification/reset emails. Never hardcode these in `config.py` — they must come from the environment.
- `SUPABASE_URL` / `SUPABASE_KEY`: optional storage integration; local image storage under `static/uploads/` is used when they are absent.
- `VODAFONE_CASH_NUMBER` / `INSTAPAY_ID`: payment details shown on the course/book payment pages.

## Database compatibility
The application runs `create_all()` and includes lightweight migrations for older databases: `user.grade_id`, `bookings.user_id`, and indexes on foreign-key columns. These migrations use ANSI-standard-enough SQL (`ALTER TABLE ... ADD COLUMN`, `CREATE INDEX IF NOT EXISTS`) that work on both SQLite and MySQL.
