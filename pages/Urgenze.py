import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import openpyxl


st.title("Urgenze di rifornimento")
st.write("In questa sezione, i dati del magazzino vengono confrontati con i dati delle proiezioni e evidenziano i maggiori bisogni prossimi delle affiliate messe in ordine per urgenza.")
df = pd.read_excel("DB_mockup.xlsx")
negozi_unici = df["Negozio"].unique().tolist()

with st.sidebar:
    negozio = st.selectbox(
        "Negozi",
        negozi_unici
    )


df_alert = df[df.columns[1050:]]
df_alert['Necessario'] = df_alert.iloc[:, :60].sum(axis=1)

df_alert = df_alert[["Necessario","Magazzino","Negozio","Prodotto"]]
df_alert = df_alert[df_alert['Magazzino'] < df_alert['Necessario']]

df_alert = df_alert[df_alert["Negozio"]==negozio]


st.dataframe(df_alert)
# Imposta il numero di colonne per i grafici
num_colonne = 3

# Calcola il numero totale di righe e suddividilo per il numero di colonne
num_righe = len(df_alert)
num_grafici_per_colonna = (num_righe + num_colonne - 1) // num_colonne

df_alert["Necessario"] = df_alert["Necessario"].round()
width = 250  # Larghezza
height = 500  # Altezza
title_font_size = 10

df_alert["Differenza"] = df_alert["Necessario"] - df_alert["Magazzino"]
df_alert = df_alert.sort_values(by="Differenza",ascending=False)



df_alert_plot = df_alert.head(9)


# Itera sul DataFrame e crea tre grafici affiancati orizzontalmente per ogni riga

for i in range(num_grafici_per_colonna):
    a = 1
    col1, col2, col3 = st.columns(3)

    start_idx = i * num_colonne
    end_idx = min((i + 1) * num_colonne, num_righe)

    # Estrai i dati per i tre grafici attuali
    data_slice = df_alert_plot.iloc[start_idx:end_idx]

    for index, row in data_slice.iterrows():
        fig = px.bar(
            pd.DataFrame({'Categoria': ['Magazzino', 'Necessario'],
                          'Valore': [row['Magazzino'], row['Necessario']]}),
            x='Categoria',
            y='Valore',
            color='Categoria',
            text='Valore',
            title=row['Prodotto'],
            template='plotly_dark'
        )
        fig.update_layout(width=width, height=height)
        fig.update_layout(title={'text': row['Prodotto'], 'font_size': title_font_size})
        fig.update_layout(showlegend=False)



        # Utilizza le colonne st per visualizzare i grafici affiancati
        if a == 1:
            col1.plotly_chart(fig)
        elif a == 2:
            col2.plotly_chart(fig)
        elif a == 3:
            col3.plotly_chart(fig)

        # Incrementa il valore di 'a' o riportalo a 1 quando necessario
        if a != 3:
            a += 1
        else:
            a = 1
