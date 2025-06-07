import pandas as pd

#df = pd.read_csv("data/dvf/ValeursFoncieres-2024.txt", sep="|", encoding="utf-8")
df = pd.read_csv("data/dvf/dvf-2024.csv")
df["Valeur fonciere"] = pd.to_numeric(df["Valeur fonciere"])

top5_unique = df["Valeur fonciere"].dropna().unique()
top5_unique = sorted(top5_unique, reverse=True)[:5]

print(top5_unique)