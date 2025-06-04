import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.get_cad import adresse_vers_parcelle
from utils.constants import years

# Liste des noms de famille
data = pd.read_csv("data/clients.csv")

st.title("Recherche avec autocomplétion")


# Champ de recherche
recherche = st.text_input("Tapez les premières lettres d’un nom :")

noms = data["nom"].unique()
# Filtrage basé sur les premières lettres (insensible à la casse)
suggestions = [
    nom for nom in noms if nom.lower().startswith(recherche.lower())
] if recherche else []

# Affichage des suggestions si la recherche n'est pas vide
if suggestions:
    selection = st.selectbox("Suggestions :", suggestions)
    st.write(f"Nom sélectionné : **{selection}**")
    addresses = data[data["nom"] == selection]["adresse"]
    for address in addresses:
        cad = adresse_vers_parcelle(address)
        df = pd.read_csv("data/cadastre_avg.csv")
        row = df[df['Cadastre'] == cad]
        if not row.empty:
            values = row[years].values.flatten()
            fig, ax = plt.subplots()
            ax.plot(years, values, marker='o')
            ax.set_title(f"Valeur foncière pour le {address} par année")
            ax.set_xlabel("Année")
            ax.set_ylabel("Valeur foncière")
            st.pyplot(fig)
            st.write(f"En 2024, ce bien valait {round(row['2024'].values[0])}€ par mètre carré.")
            st.write(f"En 2023, ce bien valait {round(row['2023'].values[0])}€ par mètre carré.")
elif recherche:
    st.write("Aucun nom correspondant.")
