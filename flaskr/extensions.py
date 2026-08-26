"""
Shared app extensions: the MySQL connection pool and CSRF protection.
Pulled out of app.py into its own module so every blueprint can import
the same get_db()/get_cursor() without circular imports.
"""
import os
from flask import g
from flask_wtf import CSRFProtect
from mysql.connector import pooling

csrf = CSRFProtect()

_db_pool = None


def init_db_pool(app):
    global _db_pool
    db_password = os.environ.get('DB_PASSWORD')
    if not db_password:
        raise RuntimeError(
            "DB_PASSWORD is not set. Create a .env file (see .env.example) "
            "with your real MySQL credentials before running the app."
        )
    _db_pool = pooling.MySQLConnectionPool(
        pool_name="fortune_pool",
        pool_size=5,
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'root'),
        password=db_password,
        database=os.environ.get('DB_NAME', 'fortune_association'),
    )

    @app.teardown_appcontext
    def close_db(exception=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()  # returns the connection to the pool


def get_db():
    if 'db' not in g:
        g.db = _db_pool.get_connection()
    return g.db


def get_cursor():
    return get_db().cursor(dictionary=True)
