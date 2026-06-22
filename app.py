import streamlit as st
from fredapi import Fred
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Dashboard Macro", layout="wide", page_icon="📊")
st.title("🇺🇸 Dashboard Macroéconomique - États-Unis")
st.caption("Données en temps réel via FRED (Federal Reserve)")

fred = Fred(api_key=st.secrets["FRED_API_KEY"])

@st.cache_data(ttl=3600)
def charger_donnees_us():
    data = {
        'cpi': fred.get_series('CPIAUCSL').pct_change(periods=12) * 100,
        'core_cpi': fred.get_series('CPILFESL').pct_change(periods=12) * 100,
        'chomage': fred.get_series('UNRATE'),
        'taux_fed': fred.get_series('FEDFUNDS'),
        'pib': fred.get_series('GDP').pct_change(periods=4) * 100,
        'retail': fred.get_series('RSAFS').pct_change(periods=12) * 100,
        'manu': fred.get_series('IPMAN').pct_change(periods=12) * 100,
        'indus': fred.get_series('INDPRO').pct_change(periods=12) * 100,
        'confiance': fred.get_series('UMCSENT'),
    }
    return {k: v.last('5Y') for k, v in data.items()}

d = charger_donnees_us()

fig = make_subplots(rows=3, cols=3, subplot_titles=(
    'Inflation CPI (%)', 'Core CPI (%)', 'Chômage (%)',
    'Taux Fed (%)', 'PIB variation (%)', 'Retail Sales (%)',
    'Prod. Manufacturière (%)', 'Prod. Industrielle (%)', 'Confiance Conso (indice)'
))

couleurs = ['#6C63FF', '#9C88FF', '#00D4AA', '#FFD166', '#FF6B6B', '#4ECDC4', '#FF9F43', '#EE5A6F', '#A29BFE']
cles = ['cpi', 'core_cpi', 'chomage', 'taux_fed', 'pib', 'retail', 'manu', 'indus', 'confiance']
positions = [(1,1),(1,2),(1,3),(2,1),(2,2),(2,3),(3,1),(3,2),(3,3)]

for cle, couleur, (r, c) in zip(cles, couleurs, positions):
    serie = d[cle]
    fig.add_trace(go.Scatter(x=serie.index, y=serie.values,
                  line=dict(color=couleur, width=2)), row=r, col=c)

fig.update_layout(template='plotly_dark', height=900, showlegend=False)
st.plotly_chart(fig, use_container_width=True)

if st.button("🔄 Rafraîchir les données"):
    st.cache_data.clear()
    st.rerun()
