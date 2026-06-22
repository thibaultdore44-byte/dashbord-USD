import streamlit as st
from fredapi import Fred
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Zone Euro", layout="wide", page_icon="🇪🇺")
st.title("🇪🇺 Dashboard Macroéconomique - Zone Euro")
st.caption("Données en temps réel via FRED")

fred = Fred(api_key=st.secrets["FRED_API_KEY"])

@st.cache_data(ttl=3600)
def charger_donnees_euro():
    data = {
        'inflation': fred.get_series('CP0000EZ19M086NEST').pct_change(periods=12) * 100,
        'taux_bce': fred.get_series('ECBDFR'),
        'chomage': fred.get_series('LRHUTTTTEZM156S'),
        'pib': fred.get_series('CLVMNACSCAB1GQEA19').pct_change(periods=4) * 100,
    }
    return {k: v.last('5Y') for k, v in data.items()}

d = charger_donnees_euro()

fig = make_subplots(rows=2, cols=2, subplot_titles=(
    'Inflation HICP (%)', 'Taux directeur BCE (%)',
    'Chômage (%)', 'PIB variation (%)'
))

couleurs = ['#6C63FF', '#FFD166', '#00D4AA', '#FF6B6B']
cles = ['inflation', 'taux_bce', 'chomage', 'pib']
positions = [(1,1),(1,2),(2,1),(2,2)]

for cle, couleur, (r, c) in zip(cles, couleurs, positions):
    serie = d[cle]
    fig.add_trace(go.Scatter(x=serie.index, y=serie.values,
                  line=dict(color=couleur, width=2)), row=r, col=c)

fig.update_layout(template='plotly_dark', height=700, showlegend=False)
st.plotly_chart(fig, use_container_width=True)

if st.button("🔄 Rafraîchir les données"):
    st.cache_data.clear()
    st.rerun()
