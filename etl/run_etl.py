"""
ETL pipeline for the Fortune Association event data.

EXTRACT  -> pull raw rows from `events` (joined with `academics`)
TRANSFORM -> aggregate with pandas: events per academic year, events per category
LOAD      -> write the aggregates into analytics_* summary tables
            -> also render two chart PNGs into flaskr/static/analytics/

Run manually with:
    python etl/run_etl.py

This is intentionally a plain script, run on demand - the next step (once
you've covered Airflow in your DE roadmap) is wrapping this same logic into
an Airflow DAG that runs it on a schedule instead of by hand. The
EXTRACT / TRANSFORM / LOAD functions below are written so that wrapping is a
straight lift-and-shift, not a rewrite.
"""
import os
import sys
from datetime import datetime

import matplotlib
matplotlib.use('Agg')  # no display needed, we're just saving PNGs
import matplotlib.pyplot as plt
import pandas as pd
from dotenv import load_dotenv
import mysql.connector

# Load .env from the project root regardless of where this script is run from
load_dotenv()

STATIC_DIR = os.path.join(os.path.dirname(__file__), '..', 'flaskr', 'static', 'analytics')


def get_connection():
    db_password = os.environ.get('DB_PASSWORD')
    if not db_password:
        print("ERROR: DB_PASSWORD not set. Make sure your .env file is filled in.")
        sys.exit(1)
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'root'),
        password=db_password,
        database=os.environ.get('DB_NAME', 'fortune_association'),
    )


def extract(conn):
    """Pull raw event + academic year data into a DataFrame."""
    query = """
        SELECT e.event_id, e.event_name, e.event_category, e.event_date,
               a.academic_year
        FROM events e
        JOIN academics a ON e.academic_id = a.academic_id
    """
    df = pd.read_sql(query, conn)
    print(f"[EXTRACT] Pulled {len(df)} event rows")
    return df


def transform(df):
    """Aggregate into two summary tables."""
    if df.empty:
        print("[TRANSFORM] No event data yet - add some events before running the ETL.")
        return pd.DataFrame(columns=['academic_year', 'event_count']), \
               pd.DataFrame(columns=['event_category', 'event_count'])

    by_year = (
        df.groupby('academic_year')
        .size()
        .reset_index(name='event_count')
        .sort_values('academic_year')
    )
    by_category = (
        df.groupby('event_category')
        .size()
        .reset_index(name='event_count')
        .sort_values('event_count', ascending=False)
    )
    print(f"[TRANSFORM] {len(by_year)} academic years, {len(by_category)} categories")
    return by_year, by_category


def load(conn, by_year, by_category, row_count):
    """Write aggregates into the analytics_* tables (full replace each run)
    and log the run."""
    cursor = conn.cursor()

    cursor.execute("DELETE FROM analytics_events_by_year")
    for _, row in by_year.iterrows():
        cursor.execute(
            "INSERT INTO analytics_events_by_year (academic_year, event_count) VALUES (%s, %s)",
            (row['academic_year'], int(row['event_count']))
        )

    cursor.execute("DELETE FROM analytics_events_by_category")
    for _, row in by_category.iterrows():
        cursor.execute(
            "INSERT INTO analytics_events_by_category (event_category, event_count) VALUES (%s, %s)",
            (row['event_category'], int(row['event_count']))
        )

    cursor.execute(
        "INSERT INTO analytics_etl_runs (rows_extracted, status, notes) VALUES (%s, %s, %s)",
        (row_count, 'success', f"Ran at {datetime.now().isoformat(timespec='seconds')}")
    )

    conn.commit()
    print(f"[LOAD] Wrote {len(by_year)} year rows, {len(by_category)} category rows. Run logged.")


def render_charts(by_year, by_category):
    os.makedirs(STATIC_DIR, exist_ok=True)

    if not by_year.empty:
        plt.figure(figsize=(7, 4))
        plt.bar(by_year['academic_year'], by_year['event_count'], color='#337ab7')
        plt.title('Events per Academic Year')
        plt.xlabel('Academic Year')
        plt.ylabel('Number of Events')
        plt.tight_layout()
        plt.savefig(os.path.join(STATIC_DIR, 'events_by_year.png'), dpi=110)
        plt.close()

    if not by_category.empty:
        plt.figure(figsize=(7, 4))
        plt.barh(by_category['event_category'], by_category['event_count'], color='#4CAF50')
        plt.title('Events per Category')
        plt.xlabel('Number of Events')
        plt.tight_layout()
        plt.savefig(os.path.join(STATIC_DIR, 'events_by_category.png'), dpi=110)
        plt.close()

    print(f"[CHARTS] Saved to {os.path.abspath(STATIC_DIR)}")


def run():
    conn = get_connection()
    try:
        df = extract(conn)
        by_year, by_category = transform(df)
        load(conn, by_year, by_category, len(df))
        render_charts(by_year, by_category)
        print("\nETL run complete.")
    except Exception as e:
        conn.rollback()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO analytics_etl_runs (rows_extracted, status, notes) VALUES (%s, %s, %s)",
            (0, 'failed', str(e)[:255])
        )
        conn.commit()
        print(f"ETL run FAILED: {e}")
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    run()
