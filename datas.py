import streamlit as st
from fredapi import Fred
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

st.set_page_config(page_title="Dashboard Macro Mondial", layout="wide", page_icon="🌍")

fred = Fred(api_key=st.secrets["FRED_API_KEY"])

# Format : 'Titre': ('code_fred', periode_variation)  | periode 0 = valeur brute
PAYS = {
    "🇺🇸 USA": {
        'Inflation CPI (%)': ('CPIAUCSL', 12),
        'Core CPI (%)': ('CPILFESL', 12),
        'Chômage (%)': ('UNRATE', 0),
        'Taux directeur (%)': ('FEDFUNDS', 0),
        'PIB variation (%)': ('GDP', 4),
        'Retail Sales (%)': ('RSAFS', 12),
    },
    "🇪🇺 Zone Euro": {
        'Inflation HICP (%)': ('CP0000EZ19M086NEST', 12),
        'Core CPI (%)': ('CPGRLE01EZM659N', 0),
        'Chômage (%)': ('LRHUTTTTEZM156S', 0),
        'Taux directeur BCE (%)': ('ECBDFR', 0),
        'PIB variation (%)': ('CLVMNACSCAB1GQEA19', 4),
        'Retail Sales (%)': ('SLRTTO01EZQ659S', 0),
    },
    "🇬🇧 UK": {
        'Inflation CPI (%)': ('GBRCPIALLMINMEI', 12),
        'Core CPI (%)': ('GBRCPICORMINMEI', 12),
        'Chômage (%)': ('LRHUTTTTGBM156S', 0),
        'Taux directeur (%)': ('IRSTCI01GBM156N', 0),
        'PIB variation (%)': ('NGDPRSAXDCGBQ', 4),
        'Retail Sales (%)': ('GBRSLRTTO02IXOBSAM', 0),
    },
    "🇯🇵 Japon": {
        'Inflation CPI (%)': ('JPNCPIALLMINMEI', 12),
        'Core CPI (%)': ('JPNCPICORMINMEI', 12),
        'Chômage (%)': ('LRHUTTTTJPM156S', 0),
        'Taux directeur (%)': ('IRSTCI01JPM156N', 0),
        'PIB variation (%)': ('JPNRGDPEXP', 4),
        'Retail Sales (%)': ('JPNSLRTTO02IXOBSAM', 0),
    },
    "🇨🇭 Suisse": {
        'Inflation CPI (%)': ('CHECPIALLMINMEI', 12),
        'Chômage (%)': ('LRHUTTTTCHM156S', 0),
        'Taux directeur (%)': ('IRSTCI01CHM156N', 0),
        'PIB variation (%)': ('CLVMNACSCAB1GQCH', 4),
    },
    "🇨🇦 Canada": {
        'Inflation CPI (%)': ('CANCPIALLMINMEI', 12),
        'Core CPI (%)': ('CANCPICORMINMEI', 12),
        'Chômage (%)': ('LRHUTTTTCAM156S', 0),
        'Taux directeur (%)': ('IRSTCI01CAM156N', 0),
        'PIB variation (%)': ('NGDPRSAXDCCAQ', 4),
    },
    "🇦🇺 Australie": {
        'Inflation CPI (%)': ('AUSCPIALLQINMEI', 4),
        'Chômage (%)': ('LRHUTTTTAUM156S', 0),
        'Taux directeur (%)': ('IRSTCI01AUM156N', 0),
        'PIB variation (%)': ('AUSGDPRQDSMEI', 4),
    },
    "🇳🇿 N-Zélande": {
        'Inflation CPI (%)': ('NZLCPIALLQINMEI', 4),
        'Chômage (%)': ('LRHUTTTTNZQ156S', 0),
        'Taux directeur (%)': ('IRSTCI01NZM156N', 0),
        'PIB variation (%)': ('NZLGDPRQDSMEI', 4),
    },
}

COULEURS = ['#6C63FF', '#9C88FF', '#00D4AA', '#FFD166', '#FF6B6B', '#4ECDC4', '#FF9F43', '#EE5A6F']

@st.cache_data(ttl=3600)
def charger_indicateur(code, periode):
    serie = fred.get_series(code)
    if periode > 0:
        serie = serie.pct_change(periods=periode) * 100
    date_limite = pd.Timestamp.now() - pd.DateOffset(years=5)
    return serie[serie.index >= date_limite]

def afficher_pays(indicateurs):
    titres = list(indicateurs.keys())
    n = len(titres)
    cols = 3
    rows = (n + cols - 1) // cols

    fig = make_subplots(rows=rows, cols=cols, subplot_titles=titres)

    for i, (titre, (code, periode)) in enumerate(indicateurs.items()):
        r = i // cols + 1
        c = i % cols + 1
        try:
            serie = charger_indicateur(code, periode)
            if len(serie) > 0:
                fig.add_trace(go.Scatter(x=serie.index, y=serie.values,
                              line=dict(color=COULEURS[i % len(COULEURS)], width=2)),
                              row=r, col=c)
        except Exception:
            pass

    fig.update_layout(template='plotly_dark', height=300*rows, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.title("🌍 Dashboard Macroéconomique Mondial")
st.caption("Données en temps réel via FRED — clique sur une économie")

noms_pays = list(PAYS.keys())
onglets = st.tabs(noms_pays)

for onglet, nom in zip(onglets, noms_pays):
    with onglet:
        afficher_pays(PAYS[nom])

if st.button("🔄 Rafraîchir toutes les données"):
    st.cache_data.clear()
    st.rerun()
