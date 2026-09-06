from models.user import User


def register(client, **overrides):
    data = {
        "name": "Ahmed Student",
        "email": "ahmed@example.com",
        "phone": "01012345678",
        "password": "password123",
        "confirm_password": "password123",
        "grade_code": "",
    }
    data.update(overrides)
    return client.post("/register", data=data, follow_redirects=False)


class TestRegister:
    def test_register_creates_unverified_user(self, client, app):
        resp = register(client)
        assert resp.status_code == 302
        assert resp.headers["Location"].endswith("/login")

        with app.app_context():
            user = User.query.filter_by(email="ahmed@example.com").first()
            assert user is not None
            assert user.is_verified is False
            assert user.role == "student"
            assert user.phone == "01012345678"

    def test_register_rejects_invalid_phone(self, client, app):
        register(client, phone="12345")

        with app.app_context():
            assert User.query.filter_by(email="ahmed@example.com").first() is None

    def test_register_rejects_mismatched_passwords(self, client, app):
        register(client, confirm_password="something-else")

        with app.app_context():
            assert User.query.filter_by(email="ahmed@example.com").first() is None

    def test_register_rejects_short_password(self, client, app):
        register(client, password="short", confirm_password="short")

        with app.app_context():
            assert User.query.filter_by(email="ahmed@example.com").first() is None

    def test_register_rejects_duplicate_email(self, client, make_user):
        make_user(email="ahmed@example.com")
        resp = register(client, follow_redirects=False)

        # Should bounce back to the register page, not create a 2nd user.
        assert resp.status_code == 302
        assert resp.headers["Location"].endswith("/register")

    def test_register_rejects_invalid_grade_code(self, client, app):
        register(client, grade_code="NOT-A-REAL-CODE")

        with app.app_context():
            assert User.query.filter_by(email="ahmed@example.com").first() is None


class TestLogin:
    def test_login_succeeds_for_verified_user(self, client, make_user, login):
        make_user(email="verified@example.com", password="password123", is_verified=True)
        resp = login("verified@example.com", "password123")
        assert resp.status_code == 302
        assert resp.headers["Location"].endswith("/dashboard")

    def test_login_blocked_for_unverified_user(self, client, make_user, login):
        make_user(email="unverified@example.com", password="password123", is_verified=False)
        resp = login("unverified@example.com", "password123")
        # Should be sent back to the login page, not logged in.
        assert resp.status_code == 302
        assert resp.headers["Location"].endswith("/login")

        # A follow-up request to a login-only page should still be anonymous.
        dash = client.get("/dashboard", follow_redirects=False)
        assert dash.status_code == 302

    def test_login_rejects_wrong_password(self, client, make_user, login):
        make_user(email="verified@example.com", password="password123")
        resp = login("verified@example.com", "wrong-password")
        assert resp.status_code == 302
        assert resp.headers["Location"].endswith("/login")

    def test_login_rejects_unknown_email(self, client, login):
        resp = login("nobody@example.com", "password123")
        assert resp.status_code == 302
        assert resp.headers["Location"].endswith("/login")

    def test_admin_login_redirects_to_admin_dashboard(self, client, make_user, login):
        make_user(email="boss@example.com", password="password123", role="admin")
        resp = login("boss@example.com", "password123")
        assert resp.status_code == 302
        assert "/admin" in resp.headers["Location"]


class TestDashboardAccess:
    def test_dashboard_requires_login(self, client):
        resp = client.get("/dashboard", follow_redirects=False)
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]

    def test_dashboard_accessible_when_logged_in(self, client, make_user, login):
        make_user(email="verified@example.com", password="password123")
        login("verified@example.com", "password123")
        resp = client.get("/dashboard")
        assert resp.status_code == 200
