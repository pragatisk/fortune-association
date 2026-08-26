from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

from ..extensions import get_db, get_cursor
from ..decorators import is_alpha, is_valid_email

bp = Blueprint('auth', __name__)


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not username or not is_alpha(username):
            flash("Username must contain only alphabetic characters", "error")
            return render_template('signup.html'), 400
        if not is_valid_email(email):
            flash("Please enter a valid email address", "error")
            return render_template('signup.html'), 400
        if len(password) < 8:
            flash("Password must be at least 8 characters", "error")
            return render_template('signup.html'), 400

        hashed_password = generate_password_hash(password)
        cursor = get_cursor()

        try:
            cursor.execute(
                "INSERT INTO user_table (user_name, email, password, role) VALUES (%s, %s, %s, %s)",
                (username, email, hashed_password, 'student')
            )
            get_db().commit()
        except mysql.connector.IntegrityError:
            get_db().rollback()
            flash("That username or email is already taken", "error")
            return render_template('signup.html'), 409
        except mysql.connector.Error as e:
            get_db().rollback()
            print(f"Signup DB error: {e}")
            flash("Something went wrong creating your account", "error")
            return render_template('signup.html'), 500

        flash("Account created — please log in.", "success")
        return redirect(url_for('auth.login_page'))

    return render_template('signup.html')


@bp.route('/login_page', methods=['GET'])
def login_page():
    return render_template('login.html')


@bp.route('/login', methods=['POST'])
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
            return redirect(url_for('academics.add_academics'))
        return redirect(url_for('live.current_events'))

    flash("Invalid credentials", "error")
    return render_template('login.html'), 401


@bp.route('/logout')
def logout():
    session.clear()
    flash("You've been logged out.", "success")
    return redirect(url_for('auth.login_page'))
