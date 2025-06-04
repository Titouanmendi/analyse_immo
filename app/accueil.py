import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.get_cad import adresse_vers_parcelle
from utils.constants import years

st.title("Evolution de la valeur foncière des appartements")
st.write("Entre l'adresse de l'appartment")

address = st.text_input("Quelle est l'adresse ?")
if address:
    cad = adresse_vers_parcelle(address)
    df = pd.read_csv("data/cadastre_avg.csv")
    row = df[df['Cadastre'] == cad]
    if not row.empty:
        values = row[years].values.flatten()
        fig, ax = plt.subplots()
        ax.plot(years, values, marker='o')
        ax.set_title("Valeur foncière en fonction de l'année")
        ax.set_xlabel("Année")
        ax.set_ylabel("Valeur foncière")
        st.pyplot(fig)
        st.write(f"Valeur en 2024: {row['2024'].values[0]}")
        st.write(f"Valeur en 2023: {row['2023'].values[0]}")
    else:
        st.write("Pas de cadastre correspondant!")
    

if st.button("Clique-moi"):
    st.write("Bouton cliqué !")
