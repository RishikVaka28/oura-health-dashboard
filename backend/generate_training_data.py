import pandas as pd
import random

# Step 1: Load CSV
df = pd.read_csv(r"R:\fitness_recommender\archive\mturkfitbit_export_4.12.16-5.12.16\Fitabase Data 4.12.16-5.12.16\dailyActivity_merged.csv")

# Step 2: Extract relevant columns
training_df = pd.DataFrame()
training_df["steps"] = df["TotalSteps"]
training_df["sleep_hours"] = df["TotalMinutesAsleep"] / 60

# Step 3: Simulate heart rate (between 65-130 bpm)
training_df["heart_rate"] = [random.randint(65, 130) for _ in range(len(df))]

# Step 4: Simulate stress level (1 = low, 5 = high)
training_df["stress_level"] = [random.randint(1, 5) for _ in range(len(df))]

# Step 5: (Optional) Simulate previous workout
training_df["previous_workout"] = random.choices(
    ["Cardio", "Strength", "Rest", "Yoga", "Walk"], k=len(df)
)

# Step 6: Create recommended workout logic
def recommend(row):
    if row["stress_level"] >= 4 or row["sleep_hours"] < 6:
        return "Rest"
    elif row["steps"] > 8000 and row["heart_rate"] < 90:
        return "Cardio"
    elif row["heart_rate"] > 100:
        return "Yoga"
    else:
        return "Strength"

training_df["recommended_workout"] = training_df.apply(recommend, axis=1)

# Step 7: Save as CSV
training_df.to_csv(r"R:\fitness_recommender\data\TrainingData.csv", index=False)
print("✅ TrainingData.csv created successfully!")
