import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from datetime import timedelta
import openpyxl

df = pd.read_excel("DB_mockup.xlsx")

st.title("Predict.ai generator")
input_settimane = st.text_input("Inserisci il numero di settimane per il quale vuoi ottenere la previsione!")

prodotti_unici = df["Prodotto"].unique().tolist()
prodotti_unici.append("Totali")

with st.sidebar:
    # Set a default value for the selectbox
    default_prodotto = "Totali"

    # Create the selectbox with the default value
    prodotto = st.selectbox(
        "Prodotti",
        prodotti_unici,
        index=prodotti_unici.index(default_prodotto) if default_prodotto in prodotti_unici else 0
    )

negozi_unici = df["Negozio"].unique().tolist()
negozi_unici.append("Totali")

with st.sidebar:
    # Set a default value for the selectbox
    default_negozio = "Totali"

    # Create the selectbox with the default value
    negozio = st.selectbox(
        "Negozi",
        negozi_unici,
        index=negozi_unici.index(default_negozio) if default_negozio in negozi_unici else 0
    )

df = df[df.columns[2:]]
melted_df = pd.melt(df, id_vars=['tipo', 'Prodotto','Negozio','Accuratezza_cat','Accuratezza num','Magazzino','Tempo di Produzione','Tempo di Spedizione'], var_name='Date', value_name='Value')
melted_df = melted_df[melted_df["tipo"]=="Previsione"]
melted_df['Date'] = pd.to_datetime(melted_df['Date'])
# Get the current date and time



genera = st.button("Genera la previsione!")

if genera:

    try:
        today_date = pd.Timestamp.now()
        weeks_to_add = int(input_settimane)

        new_date = today_date + pd.DateOffset(weeks=weeks_to_add)

        filtered_df = melted_df[(melted_df["Date"] >= today_date) & (melted_df["Date"] < new_date)]

        agg_df = filtered_df.groupby(["Negozio", "Prodotto"]).agg({
            "Value": "sum",
            "Magazzino": "sum"
        }).reset_index()
        periodo = weeks_to_add  # You may adjust this based on your needs
        agg_df["Value"] = agg_df["Value"].round()
        agg_df["Magazzino"] = agg_df["Magazzino"] / (periodo * 7)
        agg_df["Differenza"] = agg_df["Magazzino"] - agg_df["Value"]

        if negozio != "Totali" and prodotto == "Totali":
            agg_df = agg_df[agg_df["Negozio"] == negozio]

        if negozio != "Totali" and prodotto != "Totali":
            agg_df = agg_df[agg_df["Negozio"] == negozio]
            agg_df = agg_df[agg_df["Prodotto"] == prodotto]


        st.write(" ")
        st.write(" ")

        st.dataframe(agg_df)

        st.write("Genera previsione fino a data "+str(new_date)[:10])

    except:
        st.write("C'è stato un errore. Controlla di aver inserito le settimane come numero e di non aver messo un intervallo superiore a Giugno 2024!")



