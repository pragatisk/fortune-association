CREATE DATABASE IF NOT EXISTS fortune_association;
USE fortune_association;

CREATE TABLE IF NOT EXISTS user_table (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM ('admin','student') NOT NULL DEFAULT 'student'
);

CREATE TABLE IF NOT EXISTS academics (
    academic_id INT AUTO_INCREMENT PRIMARY KEY,
    academic_year VARCHAR(9) NOT NULL UNIQUE
);

-- CHANGED: event_id is now AUTO_INCREMENT instead of being typed in by the
-- admin on the Add Event form. This prevents duplicate/colliding IDs.
CREATE TABLE IF NOT EXISTS events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    academic_id INT NOT NULL,
    event_name VARCHAR(255) NOT NULL,
    event_category VARCHAR(255) NOT NULL,
    event_date DATE,
    report VARCHAR(255),
    FOREIGN KEY (academic_id) REFERENCES academics(academic_id)
        ON DELETE CASCADE,
    INDEX idx_events_academic_id (academic_id),
    INDEX idx_events_category (event_category)
);

CREATE TABLE IF NOT EXISTS current_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ename VARCHAR(255) NOT NULL,
    ecategory VARCHAR(50),
    edate DATE,
    etime TIME,
    about TEXT,
    registration_link VARCHAR(255),
    INDEX idx_current_events_date (edate)
);

-- If you already have an existing "fortune_association" database with data
-- and event_id is NOT auto-increment yet, run this instead of recreating
-- the table (backs up nothing automatically — export your data first if it matters):
--
-- ALTER TABLE events MODIFY event_id INT AUTO_INCREMENT;
