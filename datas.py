import streamlit as st
from fredapi import Fred
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

st.set_page_config(page_title="Dashboard Macro Mondial", layout="wide", page_icon="🌍")

fred = Fred(api_key=st.secrets["FRED_API_KEY"])

# ===== CONFIGURATION DES PAYS =====
# Chaque pays : nom, drapeau, et ses codes FRED par indicateur
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
        'Chômage (%)': ('LRHUTTTTEZM156S', 0),
        'Taux directeur BCE (%)': ('ECBDFR', 0),
        'PIB variation (%)': ('CLVMNACSCAB1GQEA19', 4),
    },
    "🇬🇧 UK": {
        'Inflation CPI (%)': ('GBRCPIALLMINMEI', 12),
        'Chômage (%)': ('LRHUTTTTGBM156S', 0),
        'Taux 10 ans (%)': ('IRLTLT01GBM156N', 0),
        'PIB variation (%)': ('NGDPRSAXDCGBQ', 4),
    },
    "🇯🇵 Japon": {
        'Inflation CPI (%)': ('JPNCPIALLMINMEI', 12),
        'Chômage (%)': ('LRHUTTTTJPM156S', 0),
        'Taux 10 ans (%)': ('IRLTLT01JPM156N', 0),
        'PIB variation (%)': ('JPNRGDPEXP', 4),
    },
    "🇨🇭 Suisse": {
        'Inflation CPI (%)': ('CHECPIALLMINMEI', 12),
        'Chômage (%)': ('LRHUTTTTCHM156S', 0),
        'Taux 10 ans (%)': ('IRLTLT01CHM156N', 0),
    },
    "🇨🇦 Canada": {
        'Inflation CPI (%)': ('CANCPIALLMINMEI', 12),
        'Chômage (%)': ('LRHUTTTTCAM156S', 0),
        'Taux 10 ans (%)': ('IRLTLT01CAM156N', 0),
    },
    "🇦🇺 Australie": {
        'Inflation CPI (%)': ('AUSCPIALLQINMEI', 4),
        'Chômage (%)': ('LRHUTTTTAUM156S', 0),
        'Taux 10 ans (%)': ('IRLTLT01AUM156N', 0),
    },
    "🇳🇿 N-Zélande": {
        'Inflation CPI (%)': ('NZLCPIALLQINMEI', 4),
        'Chômage (%)': ('LRHUTTTTNZQ156S', 0),
        'Taux 10 ans (%)': ('IRLTLT01NZM156N', 0),
    },
}

COULEURS = ['#6C63FF', '#9C88FF', '#00D4AA', '#FFD166', '#FF6B6B', '#4ECDC4', '#FF9F43', '#EE5A6F']

@st.cache_data(ttl=3600)
def charger_indicateur(code, periode):
    """Récupère une série FRED. Si periode > 0, calcule la variation. Sinon valeur brute."""
    serie = fred.get_series(code)
    if periode > 0:
        serie = serie.pct_change(periods=periode) * 100
    date_limite = pd.Timestamp.now() - pd.DateOffset(years=5)
    return serie[serie.index >= date_limite]

def afficher_pays(nom_pays, indicateurs):
    """Génère la grille de graphiques pour un pays."""
    titres = list(indicateurs.keys())
    n = len(titres)
    cols = 3
    rows = (n + cols - 1) // cols  # calcul du nombre de lignes nécessaires

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
            pass  # si un code FRED échoue, on saute ce graphique sans planter

    fig.update_layout(template='plotly_dark', height=300*rows, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ===== INTERFACE =====
st.title("🌍 Dashboard Macroéconomique Mondial")
st.caption("Données en temps réel via FRED — clique sur une économie")

# Créer les onglets
noms_pays = list(PAYS.keys())
onglets = st.tabs(noms_pays)

for onglet, nom in zip(onglets, noms_pays):
    with onglet:
        afficher_pays(nom, PAYS[nom])

if st.button("🔄 Rafraîchir toutes les données"):
    st.cache_data.clear()
    st.rerun()
