import streamlit as st
from fredapi import Fred
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuration de la page
st.set_page_config(page_title="Dashboard Macro US", layout="wide")
st.title("📊 Dashboard Macroéconomique US")

# Ta clé API (on verra comment la sécuriser à l'étape 4)
fred = Fred(api_key=st.secrets["FRED_API_KEY"])

# Fonction qui récupère et met en cache les données (évite de recharger à chaque fois)
@st.cache_data(ttl=3600)  # garde les données 1h en mémoire
def charger_donnees():
    cpi = fred.get_series('CPIAUCSL').pct_change(periods=12) * 100
    core_cpi = fred.get_series('CPILFESL').pct_change(periods=12) * 100
    chomage = fred.get_series('UNRATE')
    taux_fed = fred.get_series('FEDFUNDS')
    pib = fred.get_series('GDP').pct_change(periods=4) * 100
    retail = fred.get_series('RSAFS').pct_change(periods=12) * 100
    manu = fred.get_series('IPMAN').pct_change(periods=12) * 100
    indus = fred.get_series('INDPRO').pct_change(periods=12) * 100
    confiance = fred.get_series('UMCSENT')
    return cpi, core_cpi, chomage, taux_fed, pib, retail, manu, indus, confiance

# Charger les données
cpi, core_cpi, chomage, taux_fed, pib, retail, manu, indus, confiance = charger_donnees()

# Garder 5 ans
cpi, core_cpi = cpi.last('5Y'), core_cpi.last('5Y')
chomage, taux_fed = chomage.last('5Y'), taux_fed.last('5Y')
pib, retail = pib.last('5Y'), retail.last('5Y')
manu, indus, confiance = manu.last('5Y'), indus.last('5Y'), confiance.last('5Y')

# Créer la grille 3x3
fig = make_subplots(rows=3, cols=3, subplot_titles=(
    'Inflation CPI (%)', 'Core CPI (%)', 'Chômage (%)',
    'Taux Fed (%)', 'PIB variation (%)', 'Retail Sales (%)',
    'Prod. Manufacturière (%)', 'Prod. Industrielle (%)', 'Confiance Conso (indice)'
))

fig.add_trace(go.Scatter(x=cpi.index, y=cpi.values, line=dict(color='#6C63FF', width=2)), row=1, col=1)
fig.add_trace(go.Scatter(x=core_cpi.index, y=core_cpi.values, line=dict(color='#9C88FF', width=2)), row=1, col=2)
fig.add_trace(go.Scatter(x=chomage.index, y=chomage.values, line=dict(color='#00D4AA', width=2)), row=1, col=3)
fig.add_trace(go.Scatter(x=taux_fed.index, y=taux_fed.values, line=dict(color='#FFD166', width=2)), row=2, col=1)
fig.add_trace(go.Scatter(x=pib.index, y=pib.values, line=dict(color='#FF6B6B', width=2)), row=2, col=2)
fig.add_trace(go.Scatter(x=retail.index, y=retail.values, line=dict(color='#4ECDC4', width=2)), row=2, col=3)
fig.add_trace(go.Scatter(x=manu.index, y=manu.values, line=dict(color='#FF9F43', width=2)), row=3, col=1)
fig.add_trace(go.Scatter(x=indus.index, y=indus.values, line=dict(color='#EE5A6F', width=2)), row=3, col=2)
fig.add_trace(go.Scatter(x=confiance.index, y=confiance.values, line=dict(color='#A29BFE', width=2)), row=3, col=3)

fig.update_layout(template='plotly_dark', height=900, showlegend=False)

# Afficher dans la page web
st.plotly_chart(fig, use_container_width=True)

# Bouton pour rafraîchir les données
if st.button("🔄 Rafraîchir les données"):
    st.cache_data.clear()
    st.rerun()
