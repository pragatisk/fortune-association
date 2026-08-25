"""
Smoke test: mocks the MySQL layer so we can verify the Flask app boots,
all routes register, and the specific bugs we fixed don't reappear -
without needing a real MySQL server in this sandbox.
"""
import os
import sys
from unittest.mock import MagicMock, patch

os.environ['SECRET_KEY'] = 'test-key-not-for-production'
os.environ['DB_PASSWORD'] = 'test-password'
os.environ['FLASK_ENV'] = 'development'

sys.path.insert(0, 'flaskr')

with patch('mysql.connector.pooling.MySQLConnectionPool') as MockPool:
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_conn.cursor.return_value = mock_cursor
    MockPool.return_value.get_connection.return_value = mock_conn

    import app as flaskapp

    client = flaskapp.app.test_client()

    checks = []

    # 1. App boots and routes are registered
    rules = [r.rule for r in flaskapp.app.url_map.iter_rules()]
    checks.append(("App boots, routes registered", len(rules) > 10))

    # 2. Home page loads
    r = client.get('/')
    checks.append(("GET / returns 200", r.status_code == 200))

    # 3. Unauthenticated access to admin route redirects (not a crash)
    r = client.get('/current_events', follow_redirects=False)
    checks.append(("Unauth /current_events redirects (302), doesn't crash", r.status_code == 302))

    # 4. delete_event no longer accepts GET (was the unsafe pattern before)
    r = client.get('/delete_event/1')
    checks.append(("GET /delete_event/1 now rejected (405, not crash)", r.status_code == 405))

    # 5. abort is properly imported - hitting admin_required as non-admin shouldn't NameError
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['role'] = 'student'
    r = client.get('/list_academics')
    checks.append(("Non-admin hitting admin route gets clean 403 (no NameError)", r.status_code == 403))

    # 6. Signup form loads (has csrf token in it now)
    r = client.get('/signup')
    checks.append(("GET /signup returns 200", r.status_code == 200))
    checks.append(("CSRF token present in signup form", b'csrf_token' in r.data))

    print("\n--- SMOKE TEST RESULTS ---")
    all_pass = True
    for name, passed in checks:
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False
        print(f"[{status}] {name}")

    print("\nALL CHECKS PASSED" if all_pass else "\nSOME CHECKS FAILED")
    sys.exit(0 if all_pass else 1)
