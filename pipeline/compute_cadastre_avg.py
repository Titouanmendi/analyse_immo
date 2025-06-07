import pandas as pd
from utils.constants import years, dvf_path

# Initialize the merged DataFrame to None
merged_df = None

for i, year in enumerate(years):
    file = dvf_path[i]
    df = pd.read_csv(file)

    # Remove invalid or zero surface
    df = df[df["Surface reelle bati"] > 0]

    # Compute price per m²
    df["price_per_m2"] = df["Valeur fonciere"] / df["Surface reelle bati"]

    # Group by Cadastre
    grouped = df.groupby("Cadastre").agg(
        {
            "price_per_m2": "mean",
            "Cadastre": "count"
        }
    ).rename(columns={
        "price_per_m2": year,
        "Cadastre": f"transactions {year}"
    })
    
    grouped[year] = grouped[year].round(0)
    grouped = grouped.reset_index()

    # Merge with the accumulated DataFrame
    if merged_df is None:
        merged_df = grouped
    else:
        merged_df = merged_df.merge(grouped, on="Cadastre", how="outer")

# Fill missing values with 0 and sort
merged_df = merged_df.fillna(0).sort_values("Cadastre")

# Save result
merged_df.to_csv("cadastre_yearly_summary.csv", index=False)
