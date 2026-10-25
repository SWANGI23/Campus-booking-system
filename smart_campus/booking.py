# booking.py
# The booking logic (validation + rules) kept apart from the GUI.

import database
import rules


def make_booking(lecturer, campus, resource_id, date_text, time_text, hours_text):
    """Validate and save a booking. Returns (True/False, message to show the user)."""
    # ---- 1. validate the input
    if not rules.valid_date(date_text):
        return (False, 'Enter the date as YYYY-MM-DD, e.g. 2026-11-03.')
    start_min = rules.parse_time(time_text)
    if start_min == -1:
        return (False, 'Enter the start time as HH:MM using 24-hour time, e.g. 09:30.')
    try:
        hours = float(hours_text)
    except ValueError:
        return (False, 'Duration must be a number of hours, e.g. 1 or 1.5.')
    if hours <= 0:
        return (False, 'Duration must be greater than zero.')
    duration = int(round(hours * 60))

    # ---- 2. the resource must belong to the active campus
    valid_ids = []
    for (rid, name, rtype) in database.get_resources(campus):
        valid_ids.append(rid)
    if resource_id not in valid_ids:
        return (False, 'That resource does not belong to ' + campus + '.')

    # ---- 3. the booking must be in the future
    if not rules.is_future(date_text, start_min):
        return (False, 'You cannot book a time that has already started or passed.')

    # ---- 4. campus-specific booking policy
    problem = rules.check_policy(campus, start_min, duration)
    if problem != '':
        return (False, problem)
    active = database.count_future_for_lecturer(lecturer, campus, rules.today_text(), rules.now_minutes())
    problem = rules.check_active_limit(campus, active)
    if problem != '':
        return (False, problem)

    # ---- 5. prevent overlapping bookings for the same resource
    new_end = start_min + duration
    for (old_start, old_duration) in database.get_day_bookings(resource_id, date_text):
        if rules.check_overlap(start_min, new_end, old_start, old_start + old_duration):
            return (False, resource_id + ' is already booked ' + rules.format_slot(old_start, old_duration)
                    + ' on ' + date_text + '.')

    # ---- 6. save
    if database.add_booking(resource_id, campus, lecturer, date_text, start_min, duration):
        return (True, resource_id + ' booked at ' + campus + ' on ' + date_text + ', '
                + rules.format_slot(start_min, duration) + '.')
    return (False, 'The booking could not be saved. Please try again.')
