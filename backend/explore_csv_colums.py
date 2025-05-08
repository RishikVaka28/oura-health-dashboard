import pandas as pd

# Replace this with any Fitbit CSV you want to check
file_path = r"R:\fitness_recommender\archive\mturkfitbit_export_4.12.16-5.12.16\Fitabase Data 4.12.16-5.12.16\dailyActivity_merged.csv"

df = pd.read_csv(file_path)

print("🧾 Columns in file:", file_path)
print(df.columns)
