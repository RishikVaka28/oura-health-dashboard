-- database_schema.sql
-- Schema for Smart Fitness Coach DB

-- USERS TABLE
CREATE TABLE Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name TEXT,
    age INTEGER,
    gender TEXT,
    fitness_level TEXT,
    goals TEXT,
    preferred_workouts TEXT
);

-- ACTIVITY LOG TABLE (Daily Fitness Logs)
CREATE TABLE ActivityLog (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    date DATE NOT NULL,
    steps INTEGER,
    heart_rate INTEGER,
    sleep_hours REAL,
    stress_level INTEGER,
    FOREIGN KEY(user_id) REFERENCES Users(user_id)
);

-- RECOMMENDATIONS TABLE (Workout suggestions)
CREATE TABLE Recommendations (
    rec_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    date DATE NOT NULL,
    recommended_workout TEXT,
    reason TEXT,
    FOREIGN KEY(user_id) REFERENCES Users(user_id)
);

-- TRAINING DATA TABLE (for ML training purposes)
CREATE TABLE TrainingData (
    data_id INTEGER PRIMARY KEY AUTOINCREMENT,
    steps INTEGER,
    heart_rate INTEGER,
    sleep_hours REAL,
    stress_level INTEGER,
    previous_workout TEXT,
    recommended_workout TEXT
);
