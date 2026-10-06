CREATE DATABASE hostel_db;
USE hostel_db;
CREATE TABLE Warden (
  warden_id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(50) NOT NULL,
  phone VARCHAR(15) UNIQUE
);
CREATE TABLE Hostel (
  hostel_id INT PRIMARY KEY AUTO_INCREMENT,
  hostel_name VARCHAR(50) NOT NULL,
  hostel_type VARCHAR(10) NOT NULL CHECK (hostel_type IN ('Boys','Girls')),
  warden_id INT,
  FOREIGN KEY (warden_id) REFERENCES Warden(warden_id)
);
CREATE TABLE Room (
  room_id INT PRIMARY KEY AUTO_INCREMENT,
  hostel_id INT NOT NULL,
  room_no VARCHAR(10) NOT NULL,
  capacity INT NOT NULL CHECK (capacity > 0),
  room_type VARCHAR(20) NOT NULL,
  status VARCHAR(15) DEFAULT 'Available',
  UNIQUE (hostel_id, room_no),
  FOREIGN KEY (hostel_id) REFERENCES Hostel(hostel_id)
);
CREATE TABLE Student (
  student_id INT PRIMARY KEY AUTO_INCREMENT,
  roll_no VARCHAR(15) UNIQUE NOT NULL,
  name VARCHAR(50) NOT NULL,
  gender VARCHAR(10) NOT NULL,
  phone VARCHAR(15),
  email VARCHAR(60) UNIQUE,
  department VARCHAR(30) NOT NULL,
  year INT NOT NULL
);
CREATE TABLE Allocation (
  allocation_id INT PRIMARY KEY AUTO_INCREMENT,
  student_id INT NOT NULL,
  room_id INT NOT NULL,
  allocation_date DATE NOT NULL,
  vacate_date DATE,
  FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE,
  FOREIGN KEY (room_id) REFERENCES Room(room_id)
);
CREATE TABLE Payment (
  payment_id INT PRIMARY KEY AUTO_INCREMENT,
  student_id INT NOT NULL,
  amount DECIMAL(10,2) CHECK (amount > 0),
  payment_date DATE NOT NULL,
  mode VARCHAR(15),
  status VARCHAR(10) DEFAULT 'Paid',
  FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE
);
CREATE TABLE Service_Request (
  request_id INT PRIMARY KEY AUTO_INCREMENT,
  student_id INT NOT NULL,
  service_type VARCHAR(30) NOT NULL,
  description VARCHAR(200),
  request_date DATE NOT NULL,
  status VARCHAR(15) DEFAULT 'Pending',
  FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE
);
