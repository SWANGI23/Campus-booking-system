# rules.py
# Booking rules and helper functions that are kept separate from the
# rest of the system (Section 5.2 - Design for Future Expansion).
#
# TO ADD A NEW CAMPUS: add ONE entry to CAMPUS_RULES below.
# The database setup in database.py will create the campus automatically.

import datetime   # used ONLY to read today's date and the current time

ALL_CAMPUSES = 'ALL CAMPUSES'

# Dictionary of dictionaries: campus name -> that campus's booking rules.
CAMPUS_RULES = {
    'Centurion': {'max_hours': 2, 'open_hour': 8, 'close_hour': 17, 'max_active': 3},
    'Newtown': {'max_hours': 3, 'open_hour': 7, 'close_hour': 18, 'max_active': 5},
    'Polokwane': {'max_hours': 4, 'open_hour': 8, 'close_hour': 20, 'max_active': 2},
}

# List of resource types a campus administrator can choose from.
RESOURCE_TYPES = ['Computer Lab', 'Projector', 'Seminar Room', 'Presentation Equipment']

# List holding the number of days in each month (January to December).
DAYS_IN_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


# ---------------------------------------------------------------- time helpers
def format_time(minutes):
    """Turn minutes after midnight (e.g. 570) into text like '09:30'."""
    hours = minutes // 60
    mins = minutes % 60
    return '%02d:%02d' % (hours, mins)


def format_slot(start_min, duration):
    """Return a booking slot as text, e.g. '09:00-10:30'."""
    return format_time(start_min) + '-' + format_time(start_min + duration)


def is_leap_year(year):
    return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0


def valid_date(text):
    """Check that text is a real date in the form YYYY-MM-DD."""
    parts = text.split('-')
    if len(parts) != 3:
        return False
    if len(parts[0]) != 4 or len(parts[1]) != 2 or len(parts[2]) != 2:
        return False
    if not (parts[0].isdigit() and parts[1].isdigit() and parts[2].isdigit()):
        return False
    year = int(parts[0])
    month = int(parts[1])
    day = int(parts[2])
    if month < 1 or month > 12:
        return False
    days = DAYS_IN_MONTH[month - 1]
    if month == 2 and is_leap_year(year):
        days = 29
    return day >= 1 and day <= days


def parse_time(text):
    """Convert 'HH:MM' to minutes after midnight. Returns -1 if invalid."""
    parts = text.split(':')
    if len(parts) != 2 or len(parts[0]) != 2 or len(parts[1]) != 2:
        return -1
    if not (parts[0].isdigit() and parts[1].isdigit()):
        return -1
    hours = int(parts[0])
    mins = int(parts[1])
    if hours > 23 or mins > 59:
        return -1
    return hours * 60 + mins


def today_text():
    return str(datetime.date.today())          # e.g. '2026-10-25'


def now_minutes():
    now = datetime.datetime.now()
    return now.hour * 60 + now.minute


def is_future(date_text, start_min):
    """True if a booking starts after the current moment."""
    today = today_text()
    if date_text > today:                      # ISO dates compare correctly as text
        return True
    return date_text == today and start_min > now_minutes()


# ----------------------------------------------------------- booking rules
def policy_text(campus):
    """The policy line shown on every dashboard."""
    rule = CAMPUS_RULES[campus]
    return ('Policy: Max ' + str(rule['max_hours']) + 'h per booking | Open '
            + format_time(rule['open_hour'] * 60) + '-' + format_time(rule['close_hour'] * 60)
            + ' | Max ' + str(rule['max_active']) + ' active bookings per lecturer')


def check_policy(campus, start_min, duration_min):
    """Apply the selected campus's rules. Returns '' if allowed, otherwise the reason."""
    rule = CAMPUS_RULES[campus]
    if duration_min > rule['max_hours'] * 60:
        return campus + ' allows a maximum of ' + str(rule['max_hours']) + ' hour(s) per booking.'
    if start_min < rule['open_hour'] * 60 or start_min + duration_min > rule['close_hour'] * 60:
        return (campus + ' only allows bookings between ' + format_time(rule['open_hour'] * 60)
                + ' and ' + format_time(rule['close_hour'] * 60) + '.')
    return ''


def check_active_limit(campus, active_count):
    """Priority/fairness rule: limit on active bookings per lecturer."""
    limit = CAMPUS_RULES[campus]['max_active']
    if active_count >= limit:
        return campus + ' allows only ' + str(limit) + ' active bookings per lecturer.'
    return ''


def check_overlap(new_start, new_end, old_start, old_end):
    """True if the two time slots overlap."""
    if new_end <= old_start or new_start >= old_end:
        return False
    return True
