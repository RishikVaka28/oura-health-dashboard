import pandas as pd
import psycopg2


df = pd.read_csv(r"R:\fitness_recommender\data\TrainingData.csv")

conn = psycopg2.connect(
    dbname="fitness_coach",
    user="postgres",           # use your actual user
    password="password",     # use your actual password
    host="localhost",
    port="5432"
)
cur = conn.cursor()

for _, row in df.iterrows():
    cur.execute("""
        INSERT INTO TrainingData (steps, heart_rate, sleep_hours, stress_level, previous_workout, recommended_workout)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        row["steps"],
        row["heart_rate"],
        row["sleep_hours"],
        row["stress_level"],
        row["previous_workout"],
        row["recommended_workout"]
    ))

conn.commit()
cur.close()
conn.close()
print("✅ Data inserted into PostgreSQL TrainingData table successfully.")
