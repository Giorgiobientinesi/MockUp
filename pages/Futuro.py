import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import openpyxl

df = pd.read_excel("DB_mockup.xlsx")
df = df[df.columns[2:]]



st.title("Previsioni di Demand Forecasting")



#SIDEBAR
negozi_unici = df["Negozio"].unique().tolist()
negozi_unici.append("Totali")



with st.sidebar:
    negozio = st.selectbox(
        "Negozi",
        negozi_unici
    )


with st.sidebar:
    prodotto = st.selectbox(
        "Prodotti",
        list(df["Prodotto"].unique())
    )

with st.sidebar:
    IT = st.selectbox(
        "Intervallo di tempo",
       ["Settimanale","Mensile"])


start_date = datetime(2021, 1, 1)
end_date = datetime(2023, 12, 31)
st.sidebar.write(" ")
selected_date = st.sidebar.slider('Mostra dati da', start_date, end_date,step=timedelta(days=30))



# Create a date range slider
try:
    test = df[df["Prodotto"]==prodotto]

    if negozio != "Totali":
        test = test[test["Negozio"]==negozio]

    Accuratezza_cat = test["Accuratezza_cat"].iloc[0]
    Accuratezza_num	= test["Accuratezza num"].iloc[0]
    Magazzino = test["Magazzino"].iloc[0]
    Tempo_produzione = test["Tempo di Produzione"].iloc[0]
    Tempo_consegna = test["Tempo di Spedizione"].iloc[0]


    melted_df = pd.melt(test, id_vars=['tipo', 'Prodotto','Negozio','Accuratezza_cat','Accuratezza num','Magazzino','Tempo di Produzione','Tempo di Spedizione'], var_name='Date', value_name='Value')
    melted_df = melted_df[melted_df["tipo"]=="Previsione"]
    melted_df['Date'] = pd.to_datetime(melted_df['Date'])

    weekly_grouped = melted_df.set_index('Date').resample('W').sum().reset_index()
    monthly_grouped = melted_df.set_index('Date').resample('M').sum().reset_index()

    weekly_grouped = weekly_grouped[(weekly_grouped['Date'] >= selected_date)]
    monthly_grouped = monthly_grouped[(monthly_grouped['Date'] >= selected_date)]


    monthly_grouped['Color'] = monthly_grouped['Date'] > '2023-12-1'
    monthly_grouped['Color'] = monthly_grouped['Color'].map({True: 'Previsioni', False: 'Vendite'})

    monthly_line = px.line(monthly_grouped, x='Date', y='Value', color='Color',
                  labels={'Value': 'Value'},
                  title='Vendite e Previsioni Mensili ' +str(prodotto), template='plotly_dark')
    monthly_line.update_traces(line=dict(color='red'), selector=dict(name='Previsioni'))




    weekly_grouped['Color'] = weekly_grouped['Date'] > '2023-12-1'
    weekly_grouped['Color'] = weekly_grouped['Color'].map({True: 'Previsioni', False: 'Vendite'})
    weekly_line = px.line(weekly_grouped, x='Date', y='Value', color='Color',
                  labels={'Value': 'Value'},
                  title='Vendite e Previsioni Settimanali ' + str(prodotto), template='plotly_dark')
    weekly_line.update_traces(line=dict(color='red'), selector=dict(name='Previsioni'))




    filtered_df_weekly = weekly_grouped[(weekly_grouped['Date'].dt.year >= 2022)]
    filtered_df_monthly = monthly_grouped[(monthly_grouped['Date'].dt.year >= 2022)]



    if IT == "Settimanale":
        st.write(" ")
        col1, col2 = st.columns(2)

        col1.subheader("Settimanali")
        st.plotly_chart(weekly_line)

        show_data = st.button("Mostra i dati in dettaglio", key="show_data_1")
        if show_data:
            st.write(filtered_df_weekly[["Date", "Value"]])

            riduci = st.button("Riduci")
            if riduci:
                show_data = False


        col2.metric(label=Accuratezza_cat, value=str(Accuratezza_num) + "%")
    else:
        st.write(" ")
        col1, col2 = st.columns(2)

        col1.subheader("Mensili")
        st.plotly_chart(monthly_line)
        col2.metric(label=Accuratezza_cat, value=str(Accuratezza_num) + "%")

        show_data_2 = st.button("Mostra i dati in dettaglio", key="show_data_2")
        if show_data_2:
            st.write(filtered_df_monthly[["Date", "Value"]])

            riduci_2 = st.button("Riduci")
            if riduci_2:
                show_data_2 = False

    st.write(" ")
    st.write(" ")
    st.subheader("Informazioni utili")
    col1, col2 , col3 = st.columns(3)


    col1.metric(label="Rimanenze in Magazzino ", value=str(Magazzino) +" pezzi",delta=-3, delta_color="normal")
    col2.metric(label="Tempo di Produzione del prodotto ", value=str(Tempo_produzione)+" giorni")
    col3.metric(label="Tempo di spedizione del prodotto ", value=str(Tempo_consegna) + " giorni")
except:
    st.write("Non ci sono abbastanza dati per definire una previsione.")


