import streamlit as st
from fredapi import Fred
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

st.set_page_config(page_title="Royaume-Uni", layout="wide", page_icon="🇬🇧")
st.title("🇬🇧 Dashboard Macroéconomique - Royaume-Uni")
st.caption("Données en temps réel via FRED")

fred = Fred(api_key=st.secrets["FRED_API_KEY"])

@st.cache_data(ttl=3600)
def charger_donnees_uk():
    data = {
        'inflation': fred.get_series('GBRCPIALLMINMEI').pct_change(periods=12) * 100,
        'taux_boe': fred.get_series('BOERUKM'),
        'chomage': fred.get_series('LRHUTTTTGBM156S'),
        'pib': fred.get_series('CLVMNACSCAB1GQUK').pct_change(periods=4) * 100,
    }
    date_limite = pd.Timestamp.now() - pd.DateOffset(years=5)
    return {k: v[v.index >= date_limite] for k, v in data.items()}

d = charger_donnees_uk()

fig = make_subplots(rows=2, cols=2, subplot_titles=(
    'Inflation CPI (%)', 'Taux directeur BoE (%)',
    'Chômage (%)', 'PIB variation (%)'
))

couleurs = ['#6C63FF', '#FFD166', '#00D4AA', '#FF6B6B']
cles = ['inflation', 'taux_boe', 'chomage', 'pib']
positions = [(1, 1), (1, 2), (2, 1), (2, 2)]

for cle, couleur, (r, c) in zip(cles, couleurs, positions):
    serie = d[cle]
    fig.add_trace(go.Scatter(x=serie.index, y=serie.values,
                  line=dict(color=couleur, width=2)), row=r, col=c)

fig.update_layout(template='plotly_dark', height=700, showlegend=False)
st.plotly_chart(fig, use_container_width=True)

if st.button("🔄 Rafraîchir les données"):
    st.cache_data.clear()
    st.rerun()
