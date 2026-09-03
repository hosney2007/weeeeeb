# Abdelfatah Academy Web Platform

Flask educational platform with student authentication, recorded courses, bookings, school portal, assignments, admin management, PostgreSQL/Supabase support, and Vercel deployment configuration.

## Setup
1. Create a Python virtual environment.
2. Install dependencies: `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and set production secrets.
4. For production use hosted PostgreSQL (Supabase/Neon/etc.), not SQLite on Vercel.
5. Run locally with `python file.py` or with Gunicorn using `gunicorn file:app`.

## Important environment variables
- `SECRET_KEY`: stable random secret in production.
- `DATABASE_URL`: PostgreSQL connection string in production.
- `MAIL_USERNAME` / `MAIL_PASSWORD`: SMTP credentials for verification/reset emails.
- `SUPABASE_URL` / `SUPABASE_KEY`: optional storage integration; local image fallback is used when they are absent.

## Database compatibility
The application runs `create_all()` and includes lightweight migrations for older databases: `user.grade_id` and `bookings.user_id`. PostgreSQL's reserved `user` table name is correctly quoted in the migration.
