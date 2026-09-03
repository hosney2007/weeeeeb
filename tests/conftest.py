import os
import sys
import tempfile

import pytest

# --- Point the app at a throwaway database BEFORE it's imported -----------
# file.py builds the Flask app and calls db.create_all() at import time,
# so the DB target has to be set before "from file import app" runs.
# We use a real (temp) sqlite file rather than sqlite:///:memory: because
# an in-memory DB is a *new* empty database on every new connection, which
# breaks as soon as SQLAlchemy opens more than one connection.
_TEST_DB_DIR = tempfile.mkdtemp(prefix="webmaster_tests_")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_TEST_DB_DIR}/test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-prod")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from file import app as flask_app  # noqa: E402
from extinsion import db  # noqa: E402


@pytest.fixture()
def app():
    """Flask app configured for testing, with a clean DB per test."""
    flask_app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        RATELIMIT_ENABLED=False,
        MAIL_SUPPRESS_SEND=True,
        SERVER_NAME="localhost.test",
    )

    with flask_app.app_context():
        db.drop_all()
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db_session(app):
    return db.session


@pytest.fixture()
def make_user(db_session):
    """Factory fixture: make_user(email=..., role=..., is_verified=...)."""
    from werkzeug.security import generate_password_hash
    from models.user import User

    created = []

    def _make(
        name="Test User",
        email="user@example.com",
        password="password123",
        role="student",
        is_verified=True,
        grade_id=None,
    ):
        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role=role,
            is_verified=is_verified,
            grade_id=grade_id,
        )
        db_session.add(user)
        db_session.commit()
        created.append(user)
        return user

    return _make


@pytest.fixture()
def login(client):
    """Log a test client in via the real /login endpoint."""

    def _login(email, password="password123"):
        return client.post(
            "/login",
            data={"email": email, "password": password},
            follow_redirects=False,
        )

    return _login
