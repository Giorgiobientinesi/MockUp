import streamlit as st
import pandas as pd
import plotly.express as px
import openpyxl
from datetime import datetime
from itertools import combinations
from collections import defaultdict

df = pd.read_csv("Dati-generali.csv")


st.title("Analitica avanzata per la tua azienda")

st.write("In questa sezione analizziamo cose più particolari.")



transazioni = []
transazione_attuale = []
for prodotto in df['Prodotto']:
    if pd.isna(prodotto):  # Se la riga è vuota, indica la fine di una transazione
        if transazione_attuale:  # Se la transazione corrente non è vuota, aggiungila
            transazioni.append(transazione_attuale)
            transazione_attuale = []
    else:
        transazione_attuale.append(prodotto)


# Aggiungi l'ultima transazione se non è vuota
if transazione_attuale:
    transazioni.append(transazione_attuale)

coppie_di_prodotti = []
for transazione in transazioni:
    for coppia in combinations(transazione, 2):
        coppie_di_prodotti.append(list(coppia))
conteggi_cooccorrenza = defaultdict(int)

for transazione in coppie_di_prodotti:
    for prodotto1, prodotto2 in combinations(transazione, 2):
        coppia_ordinata = tuple(sorted([prodotto1, prodotto2]))
        conteggi_cooccorrenza[coppia_ordinata] += 1
df_cooccorrenza = pd.DataFrame(list(conteggi_cooccorrenza.items()), columns=['Coppia', 'Co-occorrenza'])
df_cooccorrenza.sort_values(by='Co-occorrenza', ascending=False, inplace=True)
df_cooccorrenza = df_cooccorrenza.reset_index().drop(["index"], axis=1)

df_cooccorrenza['prodotto1'] = df_cooccorrenza['Coppia'].apply(lambda x: x[0])
df_cooccorrenza['prodotto2'] = df_cooccorrenza['Coppia'].apply(lambda x: x[1])
vendite_totali = pd.concat([df_cooccorrenza['prodotto1'], df_cooccorrenza['prodotto2']]).value_counts()

def calcola_percentuale(row):
    vendite_totali_p1 = vendite_totali[row['prodotto1']]
    vendite_totali_p2 = vendite_totali[row['prodotto2']]
    percentuale_p1 = row['Co-occorrenza'] / vendite_totali_p1 * 100
    percentuale_p2 = row['Co-occorrenza'] / vendite_totali_p2 * 100
    return min(percentuale_p1, percentuale_p2)  # Usa il minore delle due percentuali per una stima conservativa

df_cooccorrenza['Percentuale'] = df_cooccorrenza.apply(calcola_percentuale, axis=1)
df_cooccorrenza_ordinato = df_cooccorrenza.sort_values(by='Percentuale', ascending=False)
df_cooccorrenza_ordinato = df_cooccorrenza_ordinato.reset_index().drop(["index"],axis=1)

top_n = 15
df_top = df_cooccorrenza_ordinato.head(top_n)

bubble = px.scatter(df_top, x='prodotto1', y='prodotto2', size='Percentuale', color='Co-occorrenza',
                 hover_name='Coppia', title='Co-occorrenza delle Coppie di Prodotti',
                 labels={'prodotto1': 'Prodotto 1', 'prodotto2': 'Prodotto 2', 'Co-occorrenza': 'Frequenza di Co-occorrenza'},
                 color_continuous_scale='Viridis')  # Cambia il nome della scala dei colori qui

# Mostra il grafico
bubble.update_layout(width=1200, height=1000)


st.header("Prodotti venduti maggiormente insieme")
# Mostra il grafico
st.plotly_chart(bubble)

scopri = st.button("Scopri di più")
if scopri:
    st.dataframe(df_top)
    Indietro = st.button("Indietro")
    if Indietro:
        scopri = False


df_pulito = df[["Data e Ora","Categoria","Nome Cliente","Sconto/Maggiorazione %","Prodotto","Quantità"]]
df_pulito = df_pulito.dropna(subset=['Quantità'])
df_pulito["Categoria"] = df_pulito["Categoria"].fillna("Altro")
df_pulito["Sconto/Maggiorazione %"] = df_pulito["Sconto/Maggiorazione %"].fillna(0)
num_na = df_pulito['Nome Cliente'].isna().sum()
num_na = df_pulito['Nome Cliente'].isna().sum()
fill_values = ["Mario"] * (num_na // 2) + ["Sara"] * (num_na // 2+1)
df_pulito.loc[df_pulito['Nome Cliente'].isna(), 'Nome Cliente'] = fill_values

df_sconti = df_pulito[["Sconto/Maggiorazione %","Prodotto","Quantità"]]
# Supponendo che il DataFrame sia già stato creato come descritto in precedenza
df_sconti['In sconto'] = df_sconti['Sconto/Maggiorazione %'].apply(lambda x: "Prezzo pieno" if x == 0 else "In sconto")
# Trova tutti i prodotti distinti nel DataFrame
prodotti_distinti = df_sconti['Prodotto'].unique()

# Inizializza una lista per memorizzare i risultati
risultati = []

# Itera attraverso ciascun prodotto
for prodotto in prodotti_distinti:
    prodotto_df = df_sconti[df_sconti['Prodotto'] == prodotto]
    media_in_sconto = prodotto_df[prodotto_df['In sconto'] == 'Prezzo pieno']['Quantità'].mean()
    media_prezzo_pieno = prodotto_df[prodotto_df['In sconto'] != 'Prezzo pieno']['Quantità'].mean()
    impatto_sconto = media_in_sconto - media_prezzo_pieno
    risultati.append({
        'Prodotto': prodotto,
        'Media Quantità in Sconto': media_in_sconto,
        'Media Quantità a Prezzo Pieno': media_prezzo_pieno,
        'Impatto dello Sconto': impatto_sconto
    })

risultati_df = pd.DataFrame(risultati)
risultati_df = risultati_df.dropna()
risultati_df["Impatto dello Sconto"] = risultati_df["Impatto dello Sconto"].round(2)

risultati_df_meno = risultati_df.sort_values(by="Impatto dello Sconto").head(10)
risultati_df_top = risultati_df.sort_values(by="Impatto dello Sconto").tail(10)


risultati_df = risultati_df.sort_values(by='Impatto dello Sconto', ascending=False)
fig_meno = px.bar(
    risultati_df_meno,
    x='Impatto dello Sconto',
    y='Prodotto',
    orientation='h',  # Grafico a barre orizzontali
    title='Prodotti con impatto negativo',
    labels={'Impatto dello Sconto': 'Impatto dello Sconto', 'Prodotto': 'Prodotto'},
    text='Impatto dello Sconto'  # Etichetta con il valore dell'impatto dello sconto
)
fig_meno.update_layout(
    xaxis_title='Prodotti con impatto positivo',
    yaxis_title='Prodotto',
    xaxis_tickangle=-45,  # Angolo delle etichette dell'asse X
    template='plotly_dark'  # Sfondo scuro
)
fig_meno.update_layout(height=600)

fig_più = px.bar(
    risultati_df_top,
    x='Impatto dello Sconto',
    y='Prodotto',
    orientation='h',  # Grafico a barre orizzontali
    title='Impatto positivo dello Sconto per Prodotto',
    labels={'Impatto dello Sconto': 'Impatto dello Sconto', 'Prodotto': 'Prodotto'},
    text='Impatto dello Sconto'  # Etichetta con il valore dell'impatto dello sconto
)
fig_più.update_layout(
    xaxis_title='Impatto dello Sconto',
    yaxis_title='Prodotto',
    xaxis_tickangle=-45,  # Angolo delle etichette dell'asse X
    template='plotly_dark'  # Sfondo scuro
)
fig_più.update_layout(height=600)

st.write(" ")
st.write(" ")
st.header("Analisi dell'impatto della scontistica")
st.write(" ")
col1, col2 = st.columns(2)
col1.plotly_chart(fig_meno, use_container_width=True)
col2.plotly_chart(fig_più, use_container_width=True)


