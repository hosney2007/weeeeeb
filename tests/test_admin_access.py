"""
Regression tests for the admin_required / login_required ordering bug.

@admin_required must always run AFTER @login_required, otherwise an
anonymous visitor gets a bare 401 instead of being redirected to the
login page like everywhere else in the app.
"""

import pytest


ADMIN_ONLY_ROUTES = [
    "/admin",
    "/admin/schedule",
]


@pytest.mark.parametrize("path", ADMIN_ONLY_ROUTES)
def test_admin_route_redirects_anonymous_user_to_login(client, path):
    resp = client.get(path, follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


@pytest.mark.parametrize("path", ADMIN_ONLY_ROUTES)
def test_admin_route_forbids_logged_in_non_admin(client, make_user, login, path):
    make_user(email="student@example.com", password="password123", role="student")
    login("student@example.com", "password123")

    resp = client.get(path, follow_redirects=False)
    assert resp.status_code == 403


@pytest.mark.parametrize("path", ADMIN_ONLY_ROUTES)
def test_admin_route_allows_admin_user(client, make_user, login, path):
    make_user(email="boss@example.com", password="password123", role="admin")
    login("boss@example.com", "password123")

    resp = client.get(path, follow_redirects=False)
    assert resp.status_code == 200
