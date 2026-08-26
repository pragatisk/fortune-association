from flask import Blueprint, render_template, request, redirect, url_for, flash
import mysql.connector

from ..extensions import get_db, get_cursor
from ..decorators import login_required, admin_required

bp = Blueprint('events', __name__)


@bp.route('/add_events', methods=['GET', 'POST'])
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

            cursor.execute(
                "INSERT INTO events (academic_id, event_name, event_category, event_date, report) "
                "VALUES (%s, %s, %s, %s, %s)",
                (academic_id, event_name, event_category, event_date, report)
            )
            get_db().commit()
            flash(f"Added event '{event_name}'", "success")
            return redirect(url_for('events.academic_details', academic_id=academic_id))
        except mysql.connector.Error as e:
            get_db().rollback()
            print(f"Add event DB error: {e}")
            flash("Could not save the event", "error")
            return render_template('add_events.html'), 500

    return render_template('add_events.html')


@bp.route('/academic_details/<int:academic_id>')
@login_required
@admin_required
def academic_details(academic_id):
    cursor = get_cursor()
    cursor.execute("SELECT * FROM events WHERE academic_id = %s ORDER BY event_date DESC", (academic_id,))
    data = cursor.fetchall()
    return render_template('academic_details.html', data=data)
