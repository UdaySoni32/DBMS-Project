# HostelFlow demo

A zero-setup desktop demo for the Hostel Accommodation and Student Services Management System described in the accompanying DBMS report.

## Requirements
- Python 3.10 or later
- Tkinter (included with most Windows Python installations)
- No third-party packages; SQLite is included with Python.

## Run
1. Extract this folder.
2. Double-click `run_demo.bat`, or run `python app.py` from this folder.
3. `hostel_demo.db` is created and seeded automatically on first launch.

To recreate the original sample database, close the app and run `python database.py --reset`.

## Verify the demo
Run `python verify_demo.py` to reset the sample database and execute the included Tkinter and SQLite integration checks. The script prints each result and leaves the window hidden during the checks.

## Modules
Wardens, Hostels, Rooms, Students, Allocations, Payments, Service Requests, and six live query reports. Each data module supports add, view, edit, delete, search, and refresh. Allocation insertion checks room capacity and prevents a student from having two active rooms. Foreign keys and data checks are enforced in SQLite.

## Database and schema
The runnable demo uses SQLite for portability and zero-setup reliability. `database.py` contains the executable SQLite schema and seed data. `schema_mysql.sql` preserves the report's MySQL 8-oriented schema concepts, including primary/foreign keys, uniqueness, checks, and cascades. The report documents the implementation distinction.

Sample data follows the names, roll numbers, hostels, payments, allocations, and requests in the submitted project source. Demo data is fictional academic sample data.
