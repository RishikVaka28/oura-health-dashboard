import psycopg2
import csv

# Step 1: Clean the CSV by replacing "None" with empty string
input_file = '../data/oura_trends.csv'
clean_file = '../data/oura_trends_cleaned.csv'

with open(input_file, 'r', encoding='utf-8') as infile, open(clean_file, 'w', newline='', encoding='utf-8') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    for row in reader:
        cleaned_row = ["" if cell == "None" else cell for cell in row]
        writer.writerow(cleaned_row)

# Step 2: Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="oura_data",
    user="postgres",
    password="password",  # 🔁 Replace with your actual password
    host="localhost",
    port=5432
)
cur = conn.cursor()

# Step 3: Re-create the table (optional if already done)
cur.execute("""
CREATE TABLE IF NOT EXISTS oura_trends (
    date DATE,
    restfulness_score INT,
    deep_sleep_score INT,
    readiness_score INT,
    resting_heart_rate_score INT,
    sleep_latency_score INT,
    low_activity_time INT,
    lowest_resting_heart_rate INT,
    medium_activity_time INT,
    temperature_trend_deviation TEXT,
    activity_balance_score INT,
    training_volume_score INT,
    sleep_latency INT,
    sleep_timing INT,
    average_hrv FLOAT,
    high_activity_time INT,
    sleep_balance_score INT,
    restless_sleep FLOAT,
    average_resting_heart_rate FLOAT,
    rest_time INT,
    long_periods_of_inactivity INT,
    hrv_balance_score INT,
    total_sleep_duration INT,
    sleep_efficiency_score INT,
    sleep_timin_score INT,
    inactive_time INT,
    previous_night_score INT,
    recovery_index_score INT,
    meet_daily_targets_score INT,
    total_sleep_score INT,
    sleep_score INT,
    temperature_deviation FLOAT,
    equivalent_walking_distance FLOAT,
    bedtime_start TEXT,
    bedtime_end TEXT,
    sleep_efficiency FLOAT,
    non_wear_time INT,
    stay_active_score INT,
    steps INT,
    activity_score INT,
    awake_time INT,
    rem_sleep_duration INT,
    rem_sleep_score INT,
    respiratory_rate FLOAT,
    deep_sleep_duration INT,
    light_sleep_duration INT,
    move_every_hour_score INT,
    activity_burn INT,
    average_met FLOAT,
    temperature_score INT,
    training_frequency_score INT,
    total_bedtime FLOAT,
    total_burn INT,
    previous_day_activity_score INT
);
""")
conn.commit()

# Step 4: Load cleaned CSV into the DB
with open(clean_file, 'r', encoding='utf-8') as f:
    cur.copy_expert("COPY oura_trends FROM STDIN WITH CSV HEADER", f)

conn.commit()
cur.close()
conn.close()

print("✅ Cleaned CSV uploaded successfully to oura_data DB!")
