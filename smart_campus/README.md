# Smart Campus Resource Booking System

**Module:** Programming 512 | **Institution:** Richfield Graduate Institution
**Language:** Python 3 (standard library only: `tkinter`, `sqlite3`, plus `datetime` for today's date)

A desktop application that lets lecturers book shared campus resources (computer labs,
projectors, seminar rooms, presentation equipment) across multiple campuses. Each campus
applies its own booking rules, and all data is stored in an SQLite database so it is kept
between runs.

---

## 1. How to run

1. Install Python 3 (Tkinter and SQLite are included, nothing else to install).
2. Unzip the project and open a terminal **inside the `smart_campus` folder**.
3. Run:

       python main.py

   (on some systems: `python3 main.py`)

The database file `campus.db` is created automatically in the same folder on the first run,
together with the three campuses, their starting resources and the starting accounts.
To reset everything, close the program and delete `campus.db`.

---

## 2. Starting logins

| Role | Username | Password | Campus |
|---|---|---|---|
| Campus Administrator | `Admin-cen` | `Cen@123` | Centurion |
| Campus Administrator | `Admin-new` | `New@123` | Newtown |
| Campus Administrator | `Admin-pol` | `Pol@123` | Polokwane |
| System Operator | `Operator` | `OperatorPass` | All campuses |
| Lecturer | *register your own* | | Any campus |

Lecturers create an account with **Register (Lecturer)** on the login page
(username: at least 4 characters, no spaces; password: at least 6 characters).

---

## 3. Project files

| File | Purpose |
|---|---|
| `main.py` | Starts the program: sets up the database, then opens the window. |
| `database.py` | All SQLite code (4 tables, every query, starting data). |
| `models.py` | Classes: `User` and its subclasses `Lecturer`, `CampusAdmin`, `SystemOperator`, plus `Resource`. |
| `rules.py` | `CAMPUS_RULES` dictionary, date/time validation, policy check, overlap check. |
| `booking.py` | The booking logic (validation and rules), kept separate from the GUI. |
| `gui.py` | The Tkinter interface: Login/Register, Campus Select, and one dashboard per role. |

---

## 4. How the program flows

**Page 1 - Login / Register.** The label reads *Currently Active Campus: NONE* until a campus is chosen.

**Page 2 - Campus selection (after every login).**
- *Lecturer:* picks any campus. The campus's policy is previewed when it is clicked.
- *Campus Administrator:* locked to their own campus. The list is disabled and the label reads
  *Active Campus: Centurion (Locked)*.
- *System Operator:* picks **ALL CAMPUSES** (system-wide) or a single campus to focus on.

**Page 3 - Dashboard.** Every dashboard header shows the user, the **active campus** and the
**booking policy in effect**.

### Lecturer
- Resource list with availability for the date typed in (shows booked time slots and **IN USE NOW**).
- Book a resource: enter date (`YYYY-MM-DD`), start time (`HH:MM`, 24-hour) and duration in hours (e.g. `1.5`).
- **My bookings** with radio buttons: Active (upcoming), Past history, Cancelled, All.
- Cancel a future active booking (saved to the database straight away).

### Campus Administrator
- Add, update and remove resources for their campus (type chosen with radio buttons).
- Click a resource in the list to load it into the form.
- Live resource list with booking counts and *Available now / IN USE NOW*.
- Usage panel: total bookings, average duration, most used resource, resources in use now, bookings per date.
- List of all bookings at the campus.

### System Operator
- **View Bookings** and **View Resources** (all campuses, or the one chosen).
- **Campus Comparison Report:** for every campus, its policy, total bookings, average duration
  (and what % of the campus's time limit that is), most used resource and usage per resource.
- **Booking Trends:** bookings per campus per date.

---

## 5. Campus booking policies

| Campus | Max length per booking | Booking hours | Max active bookings per lecturer |
|---|---|---|---|
| Centurion | 2 hours | 08:00 - 17:00 | 3 |
| Newtown | 3 hours | 07:00 - 18:00 | 5 |
| Polokwane | 4 hours | 08:00 - 20:00 | 2 |

Rules are applied automatically for the selected campus and the active policy is always displayed.

---

## 6. Validation and error handling

- Login: empty fields and wrong username/password are rejected.
- Register: length rules, matching passwords, unique username.
- Dates must be real calendar dates (leap years handled); times must be `HH:MM`; duration must be a number above zero.
- Bookings in the past are rejected.
- Campus policy (maximum length, booking hours, active-booking limit) is checked before saving.
- **Overlapping bookings for the same resource on the same date are rejected** (touching slots, e.g. 09:00-10:00 then 10:00-11:00, are allowed). Cancelled bookings do not block a slot.
- A resource must belong to the active campus to be booked.
- Duplicate resource IDs are detected (using a set of existing IDs) and rejected; IDs are stored in capitals and cannot contain spaces.
- A resource that still has future bookings cannot be removed.
- Database errors are caught with `try / except sqlite3.Error` and shown to the user as messages.

---

## 7. Database (SQLite)

| Table | Columns |
|---|---|
| `users` | username (primary key), password, role, campus |
| `campuses` | name (primary key) |
| `resources` | resource_id (primary key), name, rtype, campus |
| `bookings` | booking_id (primary key), resource_id, campus, lecturer, booking_date, start_min, duration, status |

Times are stored as minutes after midnight (09:30 = 570) and durations in minutes.
`status` is `Active` or `Cancelled`; reports count only `Active` bookings.
All values are passed with `?` placeholders.

---

## 8. Requirement checklist

| Brief section | Where it is met |
|---|---|
| 2 / 4.1 Multiple campuses in dictionaries, lists, sets | `CAMPUS_RULES` (dict), resource lists of tuples, `get_all_resource_ids()` (set) |
| 3 Roles using OOP | `models.py`: inheritance, hidden `__` attributes, overridden methods |
| 3.1 Lecturer | Register, login, campus select, book, personal history |
| 3.2 Campus Administrator | Resource add/update/remove, campus bookings, usage and availability |
| 3.3 System Operator | System-wide views and comparative reports |
| 4.1 Active campus shown | Header label on every page; "Locked" for administrators |
| 4.2 Unique resource IDs | Set check plus `PRIMARY KEY` |
| 4.3 Date, start time, duration, lecturer and campus; no overlaps | `booking.py`, `rules.check_overlap` |
| 5.1 Three campuses with different rules; policy displayed | `CAMPUS_RULES`, `rules.policy_text` |
| 5.2 Expansion | Rules live in `rules.py`; see section 9 |
| 6.1 / 6.2 Manage bookings, live availability | Lecturer dashboard |
| 7.1 / 7.2 Reports and comparisons | Admin usage panel, operator comparison and trends |
| 8 Persistence | `database.py`, `campus.db` |

---

## 9. Adding a new campus or rule

**New campus:** add one entry to `CAMPUS_RULES` in `rules.py`, for example

    'Midrand': {'max_hours': 2, 'open_hour': 9, 'close_hour': 16, 'max_active': 4},

On the next run the campus is saved to the database automatically and appears in every
campus list and report. (Optional: add starting resources in `SEED_RESOURCES` and an
administrator in `SEED_USERS` in `database.py`.)

**New rule type:** add a value to the campus dictionaries and one check function in `rules.py`,
then call it from `booking.make_booking()`. The GUI does not need to change.

---

## 10. Study-guide fundamentals used

| Chapter | Used for |
|---|---|
| 1 Lists and tuples | Lists of resources, bookings and choices; tuples for database rows, packing and unpacking |
| 2 Dictionaries and sets | `CAMPUS_RULES`, usage counts per resource, duplicate-ID set |
| 3 OOP | Classes, `__init__`, accessors, hidden attributes, inheritance, polymorphism |
| 4 Tkinter | `Tk`, `Frame`, `Label`, `Entry`, `Button`, `Listbox`, `Radiobutton`, `IntVar`, `StringVar`, `messagebox`, `pack`, `grid`, callbacks, event binding, `mainloop` |
| 5 Databases | `sqlite3.connect`, cursor, `CREATE TABLE`, `INSERT`, `SELECT`, `UPDATE`, `DELETE`, `commit`, `close`, primary and foreign keys, exception handling |

The only item outside the guide is `import datetime`, used in `rules.py` to read today's date and
the current time (needed to decide which bookings are future or past).

---

## 11. Known limitations

- Passwords are stored as plain text (hashing is outside the study guide); a real system would hash them.
- The database file is created in the folder the program is run from, so start it from inside the project folder.
- Dates and times are typed in (no calendar picker).
