from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort

from ..extensions import get_db, get_cursor
from ..decorators import login_required, admin_required

bp = Blueprint('live', __name__)

PER_PAGE = 10


@bp.route('/current_events')
@login_required
def current_events():
    page = max(1, request.args.get('page', 1, type=int))
    offset = (page - 1) * PER_PAGE

    cursor = get_cursor()
    cursor.execute("SELECT COUNT(*) AS total FROM current_events")
    total = cursor.fetchone()['total']

    cursor.execute(
        "SELECT id, ename, ecategory, edate, etime, about, registration_link "
        "FROM current_events ORDER BY edate ASC LIMIT %s OFFSET %s",
        (PER_PAGE, offset)
    )
    data = cursor.fetchall()

    total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
    return render_template(
        'current_events.html',
        data=data,
        role=session.get('role'),
        page=page,
        total_pages=total_pages
    )


@bp.route('/current_events_admin', methods=['GET', 'POST'])
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
        flash("Event added", "success")
        return redirect(url_for('live.current_events'))

    return render_template('current_events_admin.html', event=None)


@bp.route('/current_events/edit/<int:event_id>', methods=['GET', 'POST'])
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
        flash("Event updated", "success")
        return redirect(url_for('live.current_events'))

    return render_template('current_events_admin.html', event=event)


@bp.route('/delete_event/<int:event_id>', methods=['POST'])
@login_required
@admin_required
def delete_event(event_id):
    cursor = get_cursor()
    cursor.execute("DELETE FROM current_events WHERE id=%s", (event_id,))
    get_db().commit()
    flash("Event deleted", "success")
    return redirect(url_for('live.current_events'))
