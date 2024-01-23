import streamlit as st
import pandas as pd
import plotly.express as px
import openpyxl
from datetime import datetime
from itertools import combinations
from collections import defaultdict

df = pd.read_csv("Dati-generali.csv")


st.title("Analitica per la tua azienda")

st.write("In questa sezione analizziamo i prodotti della tua azienda, i loro andamenti e molto altro. Totalmente personalizzabile.")

st.header("Le vendite")

st.sidebar.toggle("Seleziona questo per analizzare prodotti specifici")


df_descrittivo = df[["Data e Ora","Categoria","Nome Cliente","Sconto/Maggiorazione %","Prodotto","Quantità"]]
df_descrittivo = df_descrittivo.dropna(subset=['Quantità'])
df_descrittivo["Categoria"] = df_descrittivo["Categoria"].fillna("Altro")
df_descrittivo["Sconto/Maggiorazione %"] = df_descrittivo["Sconto/Maggiorazione %"].fillna(0)
num_na = df_descrittivo['Nome Cliente'].isna().sum()
num_na = df_descrittivo['Nome Cliente'].isna().sum()
fill_values = ["Mario"] * (num_na // 2) + ["Sara"] * (num_na // 2+1)
df_descrittivo.loc[df_descrittivo['Nome Cliente'].isna(), 'Nome Cliente'] = fill_values
df_descrittivo["Data e Ora"] = pd.to_datetime(df_descrittivo["Data e Ora"])
df_descrittivo["Year"] = df_descrittivo["Data e Ora"].dt.year
df_descrittivo["Month"] = df_descrittivo["Data e Ora"].dt.month

with st.sidebar:
    anno = st.selectbox(
        "Anno",
        list(df_descrittivo["Year"].unique())
    )


df_anno = df_descrittivo[df_descrittivo["Year"]==anno]

df_anno = df_anno.reset_index()
df_anno = df_anno.drop(["index","Data e Ora"],axis=1)

top_categorie = df_anno.groupby("Categoria").sum().sort_values(by="Quantità",ascending=False).reset_index()[["Categoria","Quantità"]].head(10)
top_prodotto = df_anno.groupby("Prodotto").sum().sort_values(by="Quantità",ascending=False).reset_index()[["Prodotto","Quantità"]].head(10)

fig_prodotti = px.bar(
    top_prodotto,
    x="Prodotto",  # Asse X: Prodotto
    y="Quantità",  # Asse Y: Quantità
    title="Quantità per Prodotto",
    labels={"Quantità": "Quantità", "Prodotto": "Prodotto"}  # Etichette degli assi
)

# Aggiungere il layout del grafico (opzionale)
fig_prodotti.update_layout(
    xaxis_title="Prodotto",
    yaxis_title="Quantità",
    xaxis_tickangle=-45,  # Angolo delle etichette dell'asse X
    template="plotly_dark"  # Sfondo scuro
)

fig_prodotti.update_layout(
    xaxis_title="Prodotto",
    yaxis_title="Quantità",
    xaxis_tickangle=-45,  # Angolo delle etichette dell'asse X
    template="plotly_dark",  # Sfondo scuro
    height=800,  # Altezza del grafico
    font=dict(size=8),  # Dimensione del carattere delle etichette
)

fig_categorie = px.bar(
    top_categorie,
    x="Categoria",  # Asse X: Prodotto
    y="Quantità",  # Asse Y: Quantità
    title="Quantità per Categorie",
    labels={"Quantità": "Quantità", "Prodotto": "Prodotto"}  # Etichette degli assi
)

# Aggiungere il layout del grafico (opzionale)
fig_categorie.update_layout(
    xaxis_title="Prodotto",
    yaxis_title="Quantità",
    xaxis_tickangle=-45,  # Angolo delle etichette dell'asse X
    template="plotly_dark"  # Sfondo scuro
)


fig_categorie.update_layout(
    xaxis_title="Categorie",
    yaxis_title="Quantità",
    xaxis_tickangle=-45,  # Angolo delle etichette dell'asse X
    template="plotly_dark",  # Sfondo scuro
    height=800,
    font=dict(size=8),  # Dimensione del carattere delle etichette
)


col1, col2 = st.columns(2)
col1.plotly_chart(fig_prodotti, use_container_width=True)
col2.plotly_chart(fig_categorie, use_container_width=True)
