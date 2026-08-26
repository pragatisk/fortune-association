import os
from flask import Blueprint, render_template

from ..extensions import get_cursor
from ..decorators import login_required, admin_required

bp = Blueprint('analytics', __name__)


@bp.route('/analytics')
@login_required
@admin_required
def dashboard():
    cursor = get_cursor()

    cursor.execute("SELECT academic_year, event_count FROM analytics_events_by_year ORDER BY academic_year")
    by_year = cursor.fetchall()

    cursor.execute("SELECT event_category, event_count FROM analytics_events_by_category ORDER BY event_count DESC")
    by_category = cursor.fetchall()

    cursor.execute("SELECT run_at, rows_extracted, status, notes FROM analytics_etl_runs ORDER BY run_at DESC LIMIT 5")
    recent_runs = cursor.fetchall()

    static_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'analytics')
    year_chart_exists = os.path.exists(os.path.join(static_dir, 'events_by_year.png'))
    category_chart_exists = os.path.exists(os.path.join(static_dir, 'events_by_category.png'))

    return render_template(
        'analytics_dashboard.html',
        by_year=by_year,
        by_category=by_category,
        recent_runs=recent_runs,
        year_chart_exists=year_chart_exists,
        category_chart_exists=category_chart_exists,
    )
