import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("hostel_demo.db")
SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS warden (
  warden_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  phone TEXT UNIQUE
);
CREATE TABLE IF NOT EXISTS hostel (
  hostel_id INTEGER PRIMARY KEY AUTOINCREMENT,
  hostel_name TEXT NOT NULL,
  hostel_type TEXT NOT NULL CHECK(hostel_type IN ('Boys','Girls')),
  warden_id INTEGER REFERENCES warden(warden_id)
);
CREATE TABLE IF NOT EXISTS room (
  room_id INTEGER PRIMARY KEY AUTOINCREMENT,
  hostel_id INTEGER NOT NULL REFERENCES hostel(hostel_id),
  room_no TEXT NOT NULL,
  capacity INTEGER NOT NULL CHECK(capacity > 0),
  room_type TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'Available',
  UNIQUE(hostel_id, room_no)
);
CREATE TABLE IF NOT EXISTS student (
  student_id INTEGER PRIMARY KEY AUTOINCREMENT,
  roll_no TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  gender TEXT NOT NULL,
  phone TEXT,
  email TEXT UNIQUE,
  department TEXT NOT NULL,
  year INTEGER NOT NULL CHECK(year BETWEEN 1 AND 6)
);
CREATE TABLE IF NOT EXISTS allocation (
  allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER NOT NULL REFERENCES student(student_id) ON DELETE CASCADE,
  room_id INTEGER NOT NULL REFERENCES room(room_id),
  allocation_date TEXT NOT NULL,
  vacate_date TEXT
);
CREATE TABLE IF NOT EXISTS payment (
  payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER NOT NULL REFERENCES student(student_id) ON DELETE CASCADE,
  amount REAL NOT NULL CHECK(amount > 0),
  payment_date TEXT NOT NULL,
  mode TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'Paid' CHECK(status IN ('Paid','Pending','Overdue'))
);
CREATE TABLE IF NOT EXISTS service_request (
  request_id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER NOT NULL REFERENCES student(student_id) ON DELETE CASCADE,
  service_type TEXT NOT NULL,
  description TEXT NOT NULL,
  request_date TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'Pending' CHECK(status IN ('Pending','In Progress','Resolved'))
);
CREATE UNIQUE INDEX IF NOT EXISTS one_active_allocation_per_student
  ON allocation(student_id) WHERE vacate_date IS NULL;
"""

def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con

def initialize_database(reset=False):
    if reset and DB_PATH.exists():
        DB_PATH.unlink()
    con = connect()
    con.executescript(SCHEMA)
    count = con.execute("SELECT COUNT(*) FROM warden").fetchone()[0]
    if count == 0:
        con.executescript("""
        INSERT INTO warden(name,phone) VALUES
          ('Ramesh Kumar','9000000001'),('Lakshmi Devi','9000000002'),
          ('Suresh Rao','9000000003'),('Anita Singh','9000000004'),('Mohan Das','9000000005');
        INSERT INTO hostel(hostel_name,hostel_type,warden_id) VALUES
          ('Aravali Block','Boys',1),('Nilgiri Block','Girls',2),
          ('Vindhya Block','Boys',3),('Himalaya Block','Girls',4),('Sahyadri Block','Boys',5);
        INSERT INTO room(hostel_id,room_no,capacity,room_type,status) VALUES
          (1,'101',2,'Double','Available'),(1,'102',3,'Triple','Available'),
          (2,'201',2,'Double','Available'),(2,'202',1,'Single','Available'),
          (3,'301',2,'Double','Available');
        INSERT INTO student(roll_no,name,gender,phone,email,department,year) VALUES
          ('25wu0101148','Uday Soni','Male','9111111111','uday@woxsen.edu.in','CSE',1),
          ('25wu0102316','T. Sindhu','Female','9222222222','sindhu@woxsen.edu.in','CSE',1),
          ('25wu0100001','Arjun Rao','Male','9333333333','arjun@woxsen.edu.in','ECE',2),
          ('25wu0100002','Meera Nair','Female','9444444444','meera@woxsen.edu.in','BBA',1),
          ('25wu0100003','Karthik Reddy','Male','9555555555','karthik@woxsen.edu.in','CSE',3);
        INSERT INTO allocation(student_id,room_id,allocation_date,vacate_date) VALUES
          (1,1,'2026-07-15',NULL),(3,1,'2026-07-15',NULL),(2,3,'2026-07-16',NULL),
          (4,3,'2026-07-16',NULL),(5,5,'2026-07-18',NULL);
        INSERT INTO payment(student_id,amount,payment_date,mode,status) VALUES
          (1,60000,'2026-07-10','UPI','Paid'),(2,60000,'2026-07-11','Card','Paid'),
          (3,45000,'2026-07-12','Cash','Paid'),(4,60000,'2026-07-13','UPI','Paid'),
          (5,30000,'2026-07-14','Cash','Paid');
        INSERT INTO service_request(student_id,service_type,description,request_date,status) VALUES
          (1,'Maintenance','Fan not working','2026-08-01','Resolved'),
          (2,'Laundry','Laundry pickup delayed','2026-08-02','Pending'),
          (3,'Mess','Menu complaint','2026-08-03','In Progress'),
          (4,'Maintenance','Water leakage','2026-08-04','Pending'),
          (5,'Maintenance','Broken window','2026-08-05','Pending');
        """)
    con.commit()
    con.close()

if __name__ == '__main__':
    initialize_database(reset='--reset' in __import__('sys').argv)
    print(f"Database ready: {DB_PATH}")
