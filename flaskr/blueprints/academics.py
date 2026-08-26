from flask import Blueprint, render_template, request, redirect, url_for, flash
import mysql.connector

from ..extensions import get_db, get_cursor
from ..decorators import login_required, admin_required

bp = Blueprint('academics', __name__)

PER_PAGE = 12


@bp.route('/add_academics', methods=['GET', 'POST'])
@login_required
@admin_required
def add_academics():
    if request.method == 'POST':
        academic_year = request.form.get('academic_year', '').strip()
        if not academic_year:
            flash("Academic year is required", "error")
            return render_template('add_academics.html'), 400

        cursor = get_cursor()
        try:
            cursor.execute("INSERT INTO academics (academic_year) VALUES (%s)", (academic_year,))
            get_db().commit()
        except mysql.connector.IntegrityError:
            get_db().rollback()
            flash("That academic year already exists", "error")
            return render_template('add_academics.html'), 409

        flash(f"Added academic year {academic_year}", "success")
        return redirect(url_for('academics.list_academics'))

    return render_template('add_academics.html')


@bp.route('/list_academics')
@login_required
@admin_required
def list_academics():
    page = max(1, request.args.get('page', 1, type=int))
    offset = (page - 1) * PER_PAGE

    cursor = get_cursor()
    cursor.execute("SELECT COUNT(*) AS total FROM academics")
    total = cursor.fetchone()['total']

    cursor.execute(
        "SELECT academic_id, academic_year FROM academics "
        "ORDER BY academic_year DESC LIMIT %s OFFSET %s",
        (PER_PAGE, offset)
    )
    academics = cursor.fetchall()

    total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
    return render_template(
        'list_academics.html',
        academics=academics,
        page=page,
        total_pages=total_pages
    )
