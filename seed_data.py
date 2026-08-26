"""
Seeds the database with realistic dummy data so the app (and especially the
/analytics dashboard) has something to actually show.

Run from the project root, with your venv active and .env filled in:
    python seed_data.py

Safe to re-run - it checks for existing rows before inserting, so it won't
create duplicates if you run it twice.
"""
import os
import sys
from datetime import date, time

from dotenv import load_dotenv
import mysql.connector
from werkzeug.security import generate_password_hash

load_dotenv()


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


def seed_users(cursor):
    users = [
        ('admin', 'admin@fortuneassociation.test', 'Admin@1234', 'admin'),
        ('teststudent', 'student@fortuneassociation.test', 'Student@1234', 'student'),
    ]
    for username, email, password, role in users:
        cursor.execute("SELECT user_id FROM user_table WHERE user_name=%s", (username,))
        if cursor.fetchone():
            print(f"  user '{username}' already exists, skipping")
            continue
        cursor.execute(
            "INSERT INTO user_table (user_name, email, password, role) VALUES (%s,%s,%s,%s)",
            (username, email, generate_password_hash(password), role)
        )
        print(f"  created {role} user: {username} / {password}")


def seed_academics(cursor):
    years = ['2022-2023', '2023-2024', '2024-2025']
    ids = {}
    for year in years:
        cursor.execute("SELECT academic_id FROM academics WHERE academic_year=%s", (year,))
        row = cursor.fetchone()
        if row:
            ids[year] = row['academic_id']
            print(f"  academic year '{year}' already exists, skipping")
            continue
        cursor.execute("INSERT INTO academics (academic_year) VALUES (%s)", (year,))
        ids[year] = cursor.lastrowid
        print(f"  created academic year: {year}")
    return ids


def seed_events(cursor, year_ids):
    events = [
        ('2022-2023', 'Freshers Welcome', 'Cultural', date(2022, 8, 20), 'Well attended, ~200 students'),
        ('2022-2023', 'Coding Bootcamp', 'Tech', date(2022, 10, 5), 'Intro to web dev workshop'),
        ('2022-2023', 'Annual Sports Meet', 'Sports', date(2023, 2, 14), 'Cricket, athletics, badminton'),
        ('2023-2024', 'Hackathon 2023', 'Tech', date(2023, 9, 15), '48-hour hackathon, 30 teams'),
        ('2023-2024', 'Cultural Fest', 'Cultural', date(2023, 11, 10), 'Dance, music, drama competitions'),
        ('2023-2024', 'Guest Lecture: AI in Industry', 'Tech', date(2024, 1, 20), 'Industry speaker session'),
        ('2023-2024', 'Inter-college Sports Meet', 'Sports', date(2024, 2, 18), 'Hosted 6 colleges'),
        ('2024-2025', 'Hackathon 2024', 'Tech', date(2024, 9, 12), '50 teams, cloud track added'),
        ('2024-2025', 'Placement Prep Workshop', 'Career', date(2024, 10, 22), 'Resume + mock interviews'),
        ('2024-2025', 'Annual Day', 'Cultural', date(2024, 12, 5), 'Full auditorium event'),
        ('2024-2025', 'Data Science Bootcamp', 'Tech', date(2025, 1, 15), 'Python, SQL, pandas basics'),
    ]
    inserted = 0
    for year, name, category, edate, report in events:
        academic_id = year_ids[year]
        cursor.execute(
            "SELECT event_id FROM events WHERE event_name=%s AND academic_id=%s",
            (name, academic_id)
        )
        if cursor.fetchone():
            continue
        cursor.execute(
            "INSERT INTO events (academic_id, event_name, event_category, event_date, report) "
            "VALUES (%s,%s,%s,%s,%s)",
            (academic_id, name, category, edate, report)
        )
        inserted += 1
    print(f"  inserted {inserted} historical events (skipped any already present)")


def seed_current_events(cursor):
    upcoming = [
        ('Spring Hackathon 2026', 'Tech', date(2026, 9, 20), time(9, 0),
         'A 24-hour hackathon open to all departments.', 'https://example.com/register/hackathon'),
        ('Career Fair', 'Career', date(2026, 10, 3), time(10, 0),
         'Meet recruiters from 15+ companies.', 'https://example.com/register/career-fair'),
        ('Annual Sports Day', 'Sports', date(2026, 10, 25), time(8, 30),
         'Track and field events, open registration.', 'https://example.com/register/sports-day'),
    ]
    inserted = 0
    for name, category, edate, etime, about, link in upcoming:
        cursor.execute("SELECT id FROM current_events WHERE ename=%s AND edate=%s", (name, edate))
        if cursor.fetchone():
            continue
        cursor.execute(
            "INSERT INTO current_events (ename, ecategory, edate, etime, about, registration_link) "
            "VALUES (%s,%s,%s,%s,%s,%s)",
            (name, category, edate, etime, about, link)
        )
        inserted += 1
    print(f"  inserted {inserted} current/upcoming events (skipped any already present)")


def run():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    print("Seeding users...")
    seed_users(cursor)
    conn.commit()

    print("\nSeeding academic years...")
    year_ids = seed_academics(cursor)
    conn.commit()

    print("\nSeeding historical events...")
    seed_events(cursor, year_ids)
    conn.commit()

    print("\nSeeding current/upcoming events...")
    seed_current_events(cursor)
    conn.commit()

    cursor.close()
    conn.close()

    print("\nDone. Log in with:")
    print("  admin        / Admin@1234")
    print("  teststudent  / Student@1234")
    print("\nNow run: python etl/run_etl.py   -- to populate the /analytics dashboard with this data.")


if __name__ == '__main__':
    run()
