import pandas as pd
import os

directory = 'data/dvf'

frames = [pd.read_csv(file.path) for file in os.scandir(directory) if file.is_file()]

averages = []

for df in frames:
    subset = df[df["Type local"] == "Appartement"].copy()
    subset["Surface reelle bati"] = pd.to_numeric(subset["Surface reelle bati"], errors="coerce")
    subset = subset[subset["Surface reelle bati"] > 0]
    subset["Prix m2"] = subset["Valeur fonciere"] / subset["Surface reelle bati"]
    avg = subset.groupby("Cadastre")["Prix m2"].mean()
    averages.append(avg)
    
result = pd.concat(averages, axis=1)
result.columns = ["2020", "2021", "2022", "2023", "2024"]
result = result.reset_index()
result = result.rename(columns={"index": "Cadastre"})
result.to_csv("data/cadastre_avg.csv", index=False, sep=",", encoding="utf-8")