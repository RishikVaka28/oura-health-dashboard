import pandas as pd

df = pd.read_csv("../data/oura_trends.csv")
print(df.columns.tolist())
