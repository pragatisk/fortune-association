USE fortune_association;

-- Aggregate: number of events per academic year
CREATE TABLE IF NOT EXISTS analytics_events_by_year (
    academic_year VARCHAR(9) PRIMARY KEY,
    event_count INT NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Aggregate: number of events per category, across all years
CREATE TABLE IF NOT EXISTS analytics_events_by_category (
    event_category VARCHAR(255) PRIMARY KEY,
    event_count INT NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Log of every ETL run - lets you (and an interviewer) see it's a real,
-- repeatable pipeline, not a one-off script
CREATE TABLE IF NOT EXISTS analytics_etl_runs (
    run_id INT AUTO_INCREMENT PRIMARY KEY,
    run_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rows_extracted INT,
    status VARCHAR(20),
    notes VARCHAR(255)
);

select * from analytics_events_by_category;
