"""
Pytest test suite for the Flask app. Mocks MySQL entirely so these run
anywhere - your machine, CI, wherever - without a real database.

Run locally with: pytest
"""
import os
from unittest.mock import MagicMock, patch

import pytest

os.environ.setdefault('SECRET_KEY', 'test-key-not-for-production')
os.environ.setdefault('DB_PASSWORD', 'test-password')
os.environ.setdefault('FLASK_ENV', 'development')


@pytest.fixture
def client():
    with patch('mysql.connector.pooling.MySQLConnectionPool') as MockPool:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {'total': 0}
        mock_cursor.fetchall.return_value = []
        mock_conn.cursor.return_value = mock_cursor
        MockPool.return_value.get_connection.return_value = mock_conn

        from flaskr import create_app
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as c:
            yield c


def test_all_blueprint_endpoints_registered(client):
    rules = {r.endpoint for r in client.application.url_map.iter_rules()}
    expected = {
        'main.home', 'main.about', 'main.contact',
        'auth.signup', 'auth.login_page', 'auth.login', 'auth.logout',
        'academics.add_academics', 'academics.list_academics',
        'events.add_event', 'events.academic_details',
        'live.current_events', 'live.current_events_admin', 'live.edit_event', 'live.delete_event',
        'analytics.dashboard',
    }
    assert expected.issubset(rules)


def test_home_page_loads(client):
    r = client.get('/')
    assert r.status_code == 200


def test_unauth_current_events_redirects_to_login(client):
    r = client.get('/current_events', follow_redirects=False)
    assert r.status_code == 302
    assert '/login_page' in r.headers.get('Location', '')


def test_delete_event_is_post_only(client):
    """Regression test for the original bug where delete was a plain GET link."""
    r = client.get('/delete_event/1')
    assert r.status_code == 405


def test_non_admin_gets_clean_403_not_crash(client):
    """Regression test for the missing `abort` import bug."""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['role'] = 'student'
    r = client.get('/list_academics')
    assert r.status_code == 403


def test_pagination_accepts_page_param(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['role'] = 'admin'
    r = client.get('/current_events?page=2')
    assert r.status_code == 200


def test_analytics_dashboard_loads_for_admin(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['role'] = 'admin'
    r = client.get('/analytics')
    assert r.status_code == 200


def test_signup_form_has_csrf_token(client):
    r = client.get('/signup')
    assert r.status_code == 200
    assert b'csrf_token' in r.data
