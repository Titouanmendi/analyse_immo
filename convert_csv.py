import pandas as pd

file = "data/dvf_2024.csv"

df = pd.read_csv(file)

df["Code departement"] = df["Code departement"].astype(str).str.zfill(2)
df["Code commune"] = df["Code commune"].astype(str).str.zfill(3)


df["Cadastre"] = (
    df["Code departement"] +
    df["Code commune"] +
    df["Prefixe de section"].fillna("").astype(str) +
    df["Section"]
)
df = df.drop(["Identifiant de document","Reference document","1 Articles CGI","2 Articles CGI","3 Articles CGI","4 Articles CGI","5 Articles CGI","No disposition"], axis=1)

df.to_csv(file, index=False, sep=",", encoding="utf-8")