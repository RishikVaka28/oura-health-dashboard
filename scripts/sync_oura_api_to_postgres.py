import requests
import pandas as pd
import psycopg2
from datetime import datetime, timedelta, UTC
import os

OURA_TOKEN = "OURA_API_KEY"

def fetch_oura_data():
    headers = {"Authorization": f"Bearer {OURA_TOKEN}"}
    start_date = (datetime.now(UTC) - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = datetime.now(UTC).strftime("%Y-%m-%d")
    params = {"start_date": start_date, "end_date": end_date}

    def get_df(endpoint):
        url = f"https://api.ouraring.com/v2/usercollection/{endpoint}"
        r = requests.get(url, headers=headers, params=params)
        if r.status_code != 200:
            raise Exception(f"{endpoint} failed: {r.text}")
        df = pd.json_normalize(r.json()["data"])
        df['day'] = pd.to_datetime(df['day'])
        return df

    activity = get_df("daily_activity")
    sleep = get_df("daily_sleep")
    readiness = get_df("daily_readiness")

    df = activity.merge(sleep, on="day", how="outer", suffixes=("", "_sleep"))
    df = df.merge(readiness, on="day", how="outer", suffixes=("", "_readiness"))

    def get_latest_oura_timestamp(df):
        timestamps = []
        for col in ['timestamp', 'timestamp_sleep', 'timestamp_readiness']:
            if col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    timestamps.append(df[col].max())
                except Exception as e:
                    print(f"⚠️ Failed to parse column {col}: {e}")
        return max([t for t in timestamps if pd.notnull(t)], default=pd.NaT)

    latest_oura_timestamp = get_latest_oura_timestamp(df)
    if pd.notnull(latest_oura_timestamp):
        os.makedirs("../logs", exist_ok=True)
        with open("../logs/last_oura_sync.txt", "w") as f:
            f.write(latest_oura_timestamp.strftime("%Y-%m-%d %H:%M:%S"))

    return df

def safe_int(value, max_val=2_000_000_000):
    try:
        return int(min(float(value), max_val))
    except:
        return None

def safe_float(value):
    try:
        return float(value)
    except:
        return None

def sync_to_postgres(df):
    conn = psycopg2.connect(
        dbname="oura_data",
        user="postgres",
        password="password",
        host="localhost",
        port=5432
    )
    cur = conn.cursor()
    cur.execute("DELETE FROM oura_trends")

    for _, row in df.iterrows():
        cur.execute("""
            INSERT INTO oura_trends (
                date, readiness_score, sleep_score, activity_score,
                steps, sleep_efficiency, lowest_resting_heart_rate,
                total_sleep_duration, rem_sleep_duration,
                light_sleep_duration, deep_sleep_duration,
                average_hrv, temperature_deviation, activity_burn
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row.get('day'),
            safe_int(row.get('score_readiness')),
            safe_int(row.get('score_sleep')),
            safe_int(row.get('score')),
            safe_int(row.get('steps')),
            safe_float(row.get('contributors.efficiency')),
            safe_int(row.get('contributors.resting_heart_rate')),
            safe_int(row.get('contributors.total_sleep')),
            safe_int(row.get('contributors.rem_sleep')),
            safe_int(row.get('contributors.timing')),
            safe_int(row.get('contributors.deep_sleep')),
            safe_float(row.get('contributors.hrv_balance')),
            safe_float(row.get('temperature_deviation')),
            safe_int(row.get('active_calories'))
        ))

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    df = fetch_oura_data()
    sync_to_postgres(df)
    print("✅ Live Oura data synced successfully.")
