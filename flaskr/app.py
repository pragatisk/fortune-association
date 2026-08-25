# from flask import Flask, jsonify, render_template, request, redirect, url_for, session
# from datetime import datetime
# import mysql.connector
# import re
# import os
# from werkzeug.security import generate_password_hash, check_password_hash
# from functools import wraps

# app = Flask(__name__)
# app.secret_key = 'your_secret_key_here'  # Replace with a secure secret key

# # Database Configuration
# DB_HOST = os.environ.get('DB_HOST', 'localhost')
# DB_USER = os.environ.get('DB_USER', 'root')
# DB_PASSWORD = os.environ.get('DB_PASSWORD', 'Pragati@14Kadagi')
# DB_NAME = os.environ.get('DB_NAME', 'fortune_association')

# try:
#     db = mysql.connector.connect(
#         host=DB_HOST,
#         user=DB_USER,
#         password=DB_PASSWORD,
#         database=DB_NAME,
#     )
#     cursor = db.cursor(dictionary=True)
# except mysql.connector.Error as e:
#     print(f"Could not connect to MySQL: {e}")
#     db = None
#     cursor = None

# # ----------------------------
# # Helper Functions
# # ----------------------------
# def is_alpha(username):
#     return bool(re.match('^[a-zA-Z]+$', username))

# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'user_id' not in session:
#             return redirect(url_for('login_page'))
#         return f(*args, **kwargs)
#     return decorated_function

# def admin_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'role' not in session or session['role'] != 'admin':
#             return "Access Denied", 403
#         return f(*args, **kwargs)
#     return decorated_function

# # ----------------------------
# # Routes
# # ----------------------------
# @app.route('/')
# def home():
#     return render_template('index.html')

# @app.route('/about')
# def about():
#     return render_template('about.html')

# @app.route('/contact')
# def contact():
#     return render_template('contact.html')

# # Signup Route
# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         username = request.form['username']
#         email = request.form['email']
#         password = request.form['password']

#         if not username or not is_alpha(username):
#             return "Username must contain only alphabetic characters", 400
#         if len(password) < 8:
#             return "Password must be at least 8 characters", 400

#         hashed_password = generate_password_hash(password)
#         role = 'student'  # Default role

#         try:
#             cursor.execute(
#                 "INSERT INTO user_table (user_name, email, password, role) VALUES (%s, %s, %s, %s)",
#                 (username, email, hashed_password, role)
#             )
#             db.commit()
#         except Exception as e:
#             db.rollback()
#             print(e)
#             return "Error creating user", 500

#         return redirect(url_for('login_page'))

#     return render_template('signup.html')

# # Login Page
# @app.route('/login_page', methods=['GET'])
# def login_page():
#     return render_template('login.html')

# # Login Route
# @app.route('/login', methods=['POST'])
# def login():
#     username = request.form['username']
#     password = request.form['password']

#     cursor.execute("SELECT * FROM user_table WHERE user_name=%s", (username,))
#     user = cursor.fetchone()

#     if user and check_password_hash(user['password'], password):
#         session['user_id'] = user['user_id']
#         session['username'] = user['user_name']
#         session['role'] = user['role']

#         if user['role'] == 'admin':
#             return redirect(url_for('add_academics'))
#         else:
#             return redirect(url_for('current_events'))
#     else:
#         return render_template('error.html', message="Invalid credentials")

# # Logout Route
# @app.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('login_page'))

# # ----------------------------
# # Admin Routes
# # ----------------------------
# @app.route('/add_academics', methods=['GET', 'POST'])
# @login_required
# @admin_required
# def add_academics():
#     if request.method == 'POST':
#         academic_year = request.form.get('academic_year')
#         cursor.execute("INSERT INTO academics (academic_year) VALUES (%s)", (academic_year,))
#         db.commit()
#         return redirect(url_for('list_academics'))
#     return render_template('add_academics.html')

# @app.route('/list_academics')
# @login_required
# @admin_required
# def list_academics():
#     cursor.execute("SELECT academic_id, academic_year FROM academics")
#     academics = cursor.fetchall()
#     return render_template('list_academics.html', academics=academics)

# @app.route('/add_events', methods=['GET', 'POST'])
# @login_required
# @admin_required
# def add_event():
#     if request.method == 'POST':
#         try:
#             event_id = request.form['event_id']
#             academic_id = request.form['academic_id']
#             event_name = request.form['event_name']
#             event_category = request.form['event_category']
#             event_date = request.form['event_date']
#             report = request.form['report']

#             cursor.execute(
#                 "INSERT INTO events (event_id, academic_id, event_name, event_category, event_date, report) "
#                 "VALUES (%s, %s, %s, %s, %s, %s)",
#                 (event_id, academic_id, event_name, event_category, event_date, report)
#             )
#             db.commit()
#             return redirect(url_for('academic_details', academic_id=academic_id))
#         except Exception as e:
#             db.rollback()
#             return f"Error: {str(e)}", 500

#     return render_template("add_events.html")

# @app.route('/academic_details/<int:academic_id>')
# @login_required
# @admin_required
# def academic_details(academic_id):
#     cursor.execute("SELECT * FROM events WHERE academic_id = %s", (academic_id,))
#     events = cursor.fetchall()
#     data = []
#     for event in events:
#         data.append({
#             'event_id': event['event_id'],
#             'academic_id': event['academic_id'],
#             'event_name': event['event_name'],
#             'event_category': event['event_category'],
#             'event_date': event['event_date'],
#             'report': event['report']
#         })
#     return render_template('academic_details.html', data=data)

# @app.route('/current_events_admin', methods=['GET', 'POST'])
# @login_required
# def current_events_admin():
#     if session.get('role') != 'admin':
#         abort(403)

#     if request.method == 'POST':
#         cursor.execute("""
#             INSERT INTO current_events 
#             (ename, ecategory, edate, etime, about, registration_link)
#             VALUES (%s,%s,%s,%s,%s,%s)
#         """, (
#             request.form['event_name'],
#             request.form['event_category'],
#             request.form['event_date'],
#             request.form['event_time'],
#             request.form['event_about'],
#             request.form['event_registration_link']
#         ))
#         db.commit()
#         return redirect(url_for('current_events'))

#     return render_template('current_events_admin.html', event=None)

# # ----------------------------
# # Student & General Routes
# # ----------------------------

# @app.route('/current_events')
# @login_required
# def current_events():
#     cursor.execute("""
#         SELECT id, ename, ecategory, edate, etime, about, registration_link
#         FROM current_events
#     """)
#     events = cursor.fetchall()

#     data = []
#     for e in events:
#         data.append({
#             "id": e['id'],   # 👈 VERY IMPORTANT
#             "ename": e['ename'],
#             "ecategory": e['ecategory'],
#             "edate": e['edate'],
#             "etime": e['etime'],
#             "about": e['about'],
#             "registration_link": e['registration_link']
#         })

#     return render_template(
#         'current_events.html',
#         data=data,
#         role=session.get('role')   # 👈 pass role to template
#     )


# @app.route('/current_events/edit/<int:event_id>', methods=['GET', 'POST'])
# @login_required
# def edit_event(event_id):
#     if session.get('role') != 'admin':
#         abort(403)

#     cursor.execute(
#         "SELECT * FROM current_events WHERE id = %s",
#         (event_id,)
#     )
#     event = cursor.fetchone()

#     if not event:
#         abort(404)

#     if request.method == 'POST':
#         cursor.execute("""
#             UPDATE current_events
#             SET ename=%s,
#                 ecategory=%s,
#                 edate=%s,
#                 etime=%s,
#                 about=%s,
#                 registration_link=%s
#             WHERE id=%s
#         """, (
#             request.form['event_name'],
#             request.form['event_category'],
#             request.form['event_date'],
#             request.form['event_time'],
#             request.form['event_about'],
#             request.form['event_registration_link'],
#             event_id
#         ))
#         db.commit()
#         return redirect(url_for('current_events'))

#     # REUSE SAME UI (NO STYLE CHANGE)
#     return render_template('current_events_admin.html', event=event)


# @app.route('/delete_event/<int:event_id>')
# @login_required
# def delete_event(event_id):
#     if session.get('role') != 'admin':
#         abort(403)

#     cursor.execute("DELETE FROM current_events WHERE id=%s", (event_id,))
#     conn.commit()
#     return redirect(url_for('current_events'))

# # ----------------------------
# # Run App
# # ----------------------------
# if __name__ == '__main__':
#     app.run(debug=True)



import os
import re
from functools import wraps

from dotenv import load_dotenv
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, g, abort
)
from flask_wtf import CSRFProtect
import mysql.connector
from mysql.connector import pooling
from werkzeug.security import generate_password_hash, check_password_hash

# ----------------------------
# Setup
# ----------------------------
load_dotenv()  # reads variables from a local .env file (never committed)

app = Flask(__name__)

# SECRET_KEY must come from the environment now — no hardcoded fallback in
# production. In local dev, if it's missing, we generate a throwaway one and
# warn loudly, so the app doesn't silently run with a guessable key.
app.secret_key = os.environ.get('SECRET_KEY')
if not app.secret_key:
    import secrets
    app.secret_key = secrets.token_hex(32)
    print("WARNING: SECRET_KEY not set in environment. Using a temporary "
          "random key for this run only - sessions will invalidate on restart. "
          "Set SECRET_KEY in your .env file.")

csrf = CSRFProtect(app)

# ----------------------------
# Database: connection pool (fixes: connections dying after idle timeout)
# ----------------------------
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME', 'fortune_association')

if not DB_PASSWORD:
    raise RuntimeError(
        "DB_PASSWORD is not set. Create a .env file (see .env.example) "
        "with your real MySQL credentials before running the app."
    )

db_pool = pooling.MySQLConnectionPool(
    pool_name="fortune_pool",
    pool_size=5,
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
)


def get_db():
    """Get a pooled connection for this request. Opened once per request,
    closed (returned to the pool) automatically in teardown below."""
    if 'db' not in g:
        g.db = db_pool.get_connection()
    return g.db


def get_cursor():
    return get_db().cursor(dictionary=True)


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()  # returns the connection to the pool, doesn't destroy it


# ----------------------------
# Helper Functions
# ----------------------------
def is_alpha(username):
    return bool(re.match('^[a-zA-Z]+$', username))


def is_valid_email(email):
    return bool(re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email))


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


# ----------------------------
# Public Routes
# ----------------------------
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


# ----------------------------
# Auth Routes
# ----------------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not username or not is_alpha(username):
            return render_template('error.html', message="Username must contain only alphabetic characters"), 400
        if not is_valid_email(email):
            return render_template('error.html', message="Please enter a valid email address"), 400
        if len(password) < 8:
            return render_template('error.html', message="Password must be at least 8 characters"), 400

        hashed_password = generate_password_hash(password)
        role = 'student'
        cursor = get_cursor()

        try:
            cursor.execute(
                "INSERT INTO user_table (user_name, email, password, role) VALUES (%s, %s, %s, %s)",
                (username, email, hashed_password, role)
            )
            get_db().commit()
        except mysql.connector.IntegrityError:
            get_db().rollback()
            return render_template('error.html', message="That username or email is already taken"), 409
        except mysql.connector.Error as e:
            get_db().rollback()
            print(f"Signup DB error: {e}")
            return render_template('error.html', message="Something went wrong creating your account"), 500

        return redirect(url_for('login_page'))

    return render_template('signup.html')


@app.route('/login_page', methods=['GET'])
def login_page():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    cursor = get_cursor()
    cursor.execute("SELECT * FROM user_table WHERE user_name=%s", (username,))
    user = cursor.fetchone()

    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['user_id']
        session['username'] = user['user_name']
        session['role'] = user['role']

        if user['role'] == 'admin':
            return redirect(url_for('add_academics'))
        return redirect(url_for('current_events'))

    return render_template('error.html', message="Invalid credentials"), 401


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))


# ----------------------------
# Admin Routes
# ----------------------------
@app.route('/add_academics', methods=['GET', 'POST'])
@login_required
@admin_required
def add_academics():
    if request.method == 'POST':
        academic_year = request.form.get('academic_year', '').strip()
        if not academic_year:
            return render_template('error.html', message="Academic year is required"), 400

        cursor = get_cursor()
        try:
            cursor.execute("INSERT INTO academics (academic_year) VALUES (%s)", (academic_year,))
            get_db().commit()
        except mysql.connector.IntegrityError:
            get_db().rollback()
            return render_template('error.html', message="That academic year already exists"), 409

        return redirect(url_for('list_academics'))

    return render_template('add_academics.html')


@app.route('/list_academics')
@login_required
@admin_required
def list_academics():
    cursor = get_cursor()
    cursor.execute("SELECT academic_id, academic_year FROM academics ORDER BY academic_year DESC")
    academics = cursor.fetchall()
    return render_template('list_academics.html', academics=academics)


@app.route('/add_events', methods=['GET', 'POST'])
@login_required
@admin_required
def add_event():
    if request.method == 'POST':
        cursor = get_cursor()
        try:
            academic_id = request.form['academic_id']
            event_name = request.form['event_name'].strip()
            event_category = request.form['event_category'].strip()
            event_date = request.form['event_date']
            report = request.form.get('report', '').strip()

            # event_id is now auto-increment - we no longer accept it from the form
            cursor.execute(
                "INSERT INTO events (academic_id, event_name, event_category, event_date, report) "
                "VALUES (%s, %s, %s, %s, %s)",
                (academic_id, event_name, event_category, event_date, report)
            )
            get_db().commit()
            return redirect(url_for('academic_details', academic_id=academic_id))
        except mysql.connector.Error as e:
            get_db().rollback()
            print(f"Add event DB error: {e}")
            return render_template('error.html', message="Could not save the event"), 500

    return render_template("add_events.html")


@app.route('/academic_details/<int:academic_id>')
@login_required
@admin_required
def academic_details(academic_id):
    cursor = get_cursor()
    cursor.execute("SELECT * FROM events WHERE academic_id = %s ORDER BY event_date DESC", (academic_id,))
    data = cursor.fetchall()
    return render_template('academic_details.html', data=data)


@app.route('/current_events_admin', methods=['GET', 'POST'])
@login_required
@admin_required
def current_events_admin():
    if request.method == 'POST':
        cursor = get_cursor()
        cursor.execute("""
            INSERT INTO current_events
            (ename, ecategory, edate, etime, about, registration_link)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (
            request.form['event_name'],
            request.form['event_category'],
            request.form['event_date'],
            request.form['event_time'],
            request.form['event_about'],
            request.form['event_registration_link']
        ))
        get_db().commit()
        return redirect(url_for('current_events'))

    return render_template('current_events_admin.html', event=None)


# ----------------------------
# Student & General Routes
# ----------------------------
@app.route('/current_events')
@login_required
def current_events():
    cursor = get_cursor()
    cursor.execute("""
        SELECT id, ename, ecategory, edate, etime, about, registration_link
        FROM current_events
        ORDER BY edate ASC
    """)
    data = cursor.fetchall()
    return render_template('current_events.html', data=data, role=session.get('role'))


@app.route('/current_events/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_event(event_id):
    cursor = get_cursor()
    cursor.execute("SELECT * FROM current_events WHERE id = %s", (event_id,))
    event = cursor.fetchone()

    if not event:
        abort(404)

    if request.method == 'POST':
        cursor.execute("""
            UPDATE current_events
            SET ename=%s, ecategory=%s, edate=%s, etime=%s, about=%s, registration_link=%s
            WHERE id=%s
        """, (
            request.form['event_name'],
            request.form['event_category'],
            request.form['event_date'],
            request.form['event_time'],
            request.form['event_about'],
            request.form['event_registration_link'],
            event_id
        ))
        get_db().commit()
        return redirect(url_for('current_events'))

    return render_template('current_events_admin.html', event=event)


@app.route('/delete_event/<int:event_id>', methods=['POST'])
@login_required
@admin_required
def delete_event(event_id):
    cursor = get_cursor()
    cursor.execute("DELETE FROM current_events WHERE id=%s", (event_id,))
    get_db().commit()  # FIXED: was "conn.commit()" - conn was never defined
    return redirect(url_for('current_events'))


# ----------------------------
# Error handlers (so 403/404 don't show Flask's default debug page in prod)
# ----------------------------
@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', message="You don't have access to this page"), 403


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', message="Page not found"), 404


# ----------------------------
# Run App
# ----------------------------
if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug_mode)
