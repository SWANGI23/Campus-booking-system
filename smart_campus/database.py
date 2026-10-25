# database.py
# All SQLite work lives here. Pattern from the study guide:
# connect -> get a cursor -> execute -> commit -> close.
# Values are inserted with ? placeholders (never by joining strings).

import sqlite3
import rules

DB_NAME = 'campus.db'      # created in the same folder as the program

# Starting resources for each campus: campus -> list of (id, name, type) tuples.
SEED_RESOURCES = {
    'Centurion': [('CEN-LAB-01', 'Computer Lab 1', 'Computer Lab'),
                  ('CEN-LAB-02', 'Computer Lab 2', 'Computer Lab'),
                  ('CEN-PRJ-01', 'Projector A', 'Projector'),
                  ('CEN-SEM-01', 'Seminar Room 1', 'Seminar Room')],
    'Newtown': [('NEW-LAB-01', 'Computer Lab 1', 'Computer Lab'),
                ('NEW-PRJ-01', 'Projector A', 'Projector'),
                ('NEW-SEM-01', 'Seminar Room 1', 'Seminar Room'),
                ('NEW-PRE-01', 'Presentation Kit 1', 'Presentation Equipment')],
    'Polokwane': [('POL-LAB-01', 'Computer Lab 1', 'Computer Lab'),
                  ('POL-PRJ-01', 'Projector A', 'Projector'),
                  ('POL-SEM-01', 'Seminar Room 1', 'Seminar Room')],
}

# Starting accounts: (username, password, role, campus).
# NOTE: passwords are stored as plain text to keep to the study-guide content.
# A real system would store hashed passwords.
SEED_USERS = [('Admin-cen', 'Cen@123', 'CampusAdmin', 'Centurion'),
              ('Admin-new', 'New@123', 'CampusAdmin', 'Newtown'),
              ('Admin-pol', 'Pol@123', 'CampusAdmin', 'Polokwane'),
              ('Operator', 'OperatorPass', 'SystemOperator', '')]


# ------------------------------------------------------------ basic helpers
def run_write(sql, params=()):
    """Run INSERT / UPDATE / DELETE. Returns True if it worked, False if SQLite refused it."""
    conn = sqlite3.connect(DB_NAME)
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        return True
    except sqlite3.Error as err:
        print('Database error:', err)
        return False
    finally:
        conn.close()


def fetch(sql, params=()):
    """Run a SELECT and return the rows as a list of tuples."""
    conn = sqlite3.connect(DB_NAME)
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()
    except sqlite3.Error as err:
        print('Database error:', err)
        return []
    finally:
        conn.close()


# ------------------------------------------------------------------- setup
def setup_database():
    """Create the four tables and add starting data the first time the program runs."""
    run_write('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    campus TEXT)''')
    run_write('''CREATE TABLE IF NOT EXISTS campuses (
                    name TEXT PRIMARY KEY NOT NULL)''')
    run_write('''CREATE TABLE IF NOT EXISTS resources (
                    resource_id TEXT PRIMARY KEY NOT NULL,
                    name TEXT NOT NULL,
                    rtype TEXT NOT NULL,
                    campus TEXT NOT NULL,
                    FOREIGN KEY (campus) REFERENCES campuses (name))''')
    run_write('''CREATE TABLE IF NOT EXISTS bookings (
                    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    resource_id TEXT NOT NULL,
                    campus TEXT NOT NULL,
                    lecturer TEXT NOT NULL,
                    booking_date TEXT NOT NULL,
                    start_min INTEGER NOT NULL,
                    duration INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    FOREIGN KEY (resource_id) REFERENCES resources (resource_id),
                    FOREIGN KEY (campus) REFERENCES campuses (name))''')

    # Every campus listed in rules.CAMPUS_RULES gets stored in the database.
    existing = get_campus_names()
    for campus in rules.CAMPUS_RULES:
        if campus not in existing:
            run_write('INSERT INTO campuses (name) VALUES (?)', (campus,))
            for (rid, name, rtype) in SEED_RESOURCES.get(campus, []):
                add_resource(rid, name, rtype, campus)

    for (username, password, role, campus) in SEED_USERS:
        if get_user_row(username) is None:
            add_user(username, password, role, campus)


# ------------------------------------------------------------------- users
def get_user_row(username):
    rows = fetch('SELECT username, password, role, campus FROM users WHERE username = ?', (username,))
    if len(rows) == 0:
        return None
    return rows[0]


def add_user(username, password, role, campus):
    return run_write('INSERT INTO users (username, password, role, campus) VALUES (?, ?, ?, ?)',
                     (username, password, role, campus))


# --------------------------------------------------------------- campuses
def get_campus_names():
    rows = fetch('SELECT name FROM campuses ORDER BY name')
    names = []
    for row in rows:
        names.append(row[0])
    return names


# --------------------------------------------------------------- resources
def get_resources(campus):
    """List of (resource_id, name, rtype) tuples for one campus."""
    return fetch('SELECT resource_id, name, rtype FROM resources WHERE campus = ? ORDER BY resource_id',
                 (campus,))


def get_all_resources():
    """List of (resource_id, name, rtype, campus) tuples for every campus."""
    return fetch('SELECT resource_id, name, rtype, campus FROM resources ORDER BY campus, resource_id')


def get_all_resource_ids():
    """Returns a SET of every resource ID, used to detect duplicates (Section 4.2)."""
    id_set = set()
    for row in fetch('SELECT resource_id FROM resources'):
        id_set.add(row[0])
    return id_set


def add_resource(resource_id, name, rtype, campus):
    return run_write('INSERT INTO resources (resource_id, name, rtype, campus) VALUES (?, ?, ?, ?)',
                     (resource_id, name, rtype, campus))


def update_resource(resource_id, name, rtype):
    return run_write('UPDATE resources SET name = ?, rtype = ? WHERE resource_id = ?',
                     (name, rtype, resource_id))


def delete_resource(resource_id):
    return run_write('DELETE FROM resources WHERE resource_id = ?', (resource_id,))


# ---------------------------------------------------------------- bookings
def get_day_bookings(resource_id, date_text):
    """Active bookings for one resource on one date: list of (start_min, duration)."""
    return fetch('''SELECT start_min, duration FROM bookings
                    WHERE resource_id = ? AND booking_date = ? AND status = 'Active'
                    ORDER BY start_min''', (resource_id, date_text))


def add_booking(resource_id, campus, lecturer, date_text, start_min, duration):
    return run_write('''INSERT INTO bookings (resource_id, campus, lecturer, booking_date,
                                               start_min, duration, status)
                        VALUES (?, ?, ?, ?, ?, ?, 'Active')''',
                     (resource_id, campus, lecturer, date_text, start_min, duration))


def get_lecturer_bookings(lecturer):
    """(booking_id, resource_id, campus, date, start_min, duration, status) for one lecturer."""
    return fetch('''SELECT booking_id, resource_id, campus, booking_date, start_min, duration, status
                    FROM bookings WHERE lecturer = ?
                    ORDER BY booking_date, start_min''', (lecturer,))


def count_future_for_lecturer(lecturer, campus, today, now_min):
    rows = fetch('''SELECT COUNT(*) FROM bookings
                    WHERE lecturer = ? AND campus = ? AND status = 'Active'
                    AND (booking_date > ? OR (booking_date = ? AND start_min > ?))''',
                 (lecturer, campus, today, today, now_min))
    return rows[0][0]


def count_future_for_resource(resource_id, today, now_min):
    rows = fetch('''SELECT COUNT(*) FROM bookings
                    WHERE resource_id = ? AND status = 'Active'
                    AND (booking_date > ? OR (booking_date = ? AND start_min > ?))''',
                 (resource_id, today, today, now_min))
    return rows[0][0]


def cancel_booking(booking_id):
    return run_write("UPDATE bookings SET status = 'Cancelled' WHERE booking_id = ?", (booking_id,))


def get_bookings(campus):
    """All bookings for a campus, or for every campus when campus is None.
    Each row: (booking_id, resource_id, campus, lecturer, date, start_min, duration, status)."""
    columns = 'booking_id, resource_id, campus, lecturer, booking_date, start_min, duration, status'
    if campus is None:
        return fetch('SELECT ' + columns + ' FROM bookings ORDER BY campus, booking_date, start_min')
    return fetch('SELECT ' + columns + ' FROM bookings WHERE campus = ? ORDER BY booking_date, start_min',
                 (campus,))


# ----------------------------------------------------------------- reports
def campus_report(campus):
    """Returns (total bookings, average duration in minutes, most used resource row or None)."""
    total = fetch("SELECT COUNT(*) FROM bookings WHERE campus = ? AND status = 'Active'", (campus,))[0][0]
    average = fetch("SELECT AVG(duration) FROM bookings WHERE campus = ? AND status = 'Active'",
                    (campus,))[0][0]
    top_rows = fetch('''SELECT resource_id, COUNT(*) AS uses FROM bookings
                        WHERE campus = ? AND status = 'Active'
                        GROUP BY resource_id ORDER BY uses DESC LIMIT 1''', (campus,))
    top = None
    if len(top_rows) > 0:
        top = top_rows[0]
    if average is None:
        average = 0
    return (total, average, top)


def resource_usage(campus):
    """List of (resource_id, number of bookings) for a campus, busiest first."""
    return fetch('''SELECT resource_id, COUNT(*) AS uses FROM bookings
                    WHERE campus = ? AND status = 'Active'
                    GROUP BY resource_id ORDER BY uses DESC''', (campus,))


def booking_trend(campus):
    """List of (campus, date, number of bookings). campus=None means every campus."""
    if campus is None:
        return fetch('''SELECT campus, booking_date, COUNT(*) FROM bookings WHERE status = 'Active'
                        GROUP BY campus, booking_date ORDER BY campus, booking_date''')
    return fetch('''SELECT campus, booking_date, COUNT(*) FROM bookings
                    WHERE status = 'Active' AND campus = ?
                    GROUP BY campus, booking_date ORDER BY booking_date''', (campus,))
