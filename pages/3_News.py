import streamlit as st
import requests
from datetime import datetime
from deep_translator import GoogleTranslator

st.set_page_config(page_title="News", layout="wide", page_icon="📰")
st.title("📰 Flux de News Économiques")
st.caption("News financières en temps réel via NewsAPI")

# Case à cocher pour la traduction
traduire = st.checkbox("🇫🇷 Traduire les titres en français")

MOTS_FORT = ['surge', 'plunge', 'crash', 'soar', 'spike', 'shock', 'crisis',
             'recession', 'hike', 'cut rates', 'rate cut', 'rate hike',
             'inflation jumps', 'collapse', 'emergency']
MOTS_MOYEN = ['rises', 'falls', 'gains', 'drops', 'climbs', 'declines',
              'inflation', 'unemployment', 'gdp', 'fed', 'ecb', 'boe']

def evaluer_impact(titre):
    titre_min = titre.lower()
    if any(mot in titre_min for mot in MOTS_FORT):
        return "🔴", "Impact fort", "#FF6B6B"
    elif any(mot in titre_min for mot in MOTS_MOYEN):
        return "🟠", "Impact modéré", "#FFD166"
    else:
        return "🟢", "Impact faible", "#00D4AA"

@st.cache_data(ttl=1800)
def recuperer_news():
    cle = st.secrets["NEWS_API_KEY"]
    url = "https://newsapi.org/v2/everything"
    params = {
        'domains': 'reuters.com,bloomberg.com,cnbc.com,marketwatch.com,investing.com,forexlive.com,fxstreet.com',
        'language': 'en',
        'sortBy': 'publishedAt',
        'pageSize': 30,
        'apiKey': cle
    }
    response = requests.get(url, params=params)
    return response.json()

# Fonction de traduction (avec cache pour éviter de retraduire)
@st.cache_data(ttl=3600)
def traduire_texte(texte):
    if not texte:
        return texte
    try:
        return GoogleTranslator(source='auto', target='fr').translate(texte)
    except:
        return texte  # si la traduction échoue, on garde l'original

if st.button("🔄 Rafraîchir les news"):
    st.cache_data.clear()
    st.rerun()

data = recuperer_news()

if data.get('status') == 'ok':
    articles = data.get('articles', [])
    st.write(f"**{len(articles)} news récentes**")
    st.divider()

    for article in articles:
        titre = article.get('title', 'Sans titre')
        source = article.get('source', {}).get('name', 'Inconnu')
        date_str = article.get('publishedAt', '')
        url_article = article.get('url', '#')
        description = article.get('description', '')

        # Évaluer l'impact AVANT traduction (sur le texte anglais original)
        emoji, label, couleur = evaluer_impact(titre)

        # Traduire si la case est cochée
        if traduire:
            titre_affiche = traduire_texte(titre)
            description_affichee = traduire_texte(description)
        else:
            titre_affiche = titre
            description_affichee = description

        try:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            date_affichee = date_obj.strftime('%d/%m %H:%M')
        except:
            date_affichee = date_str

        st.markdown(f"""
        <div style="border-left: 4px solid {couleur}; padding: 10px 15px; 
                    margin-bottom: 12px; background-color: #1A1D2E; border-radius: 4px;">
            <div style="color: {couleur}; font-weight: bold; font-size: 13px;">
                {emoji} {label} • {source} • {date_affichee}
            </div>
            <div style="color: #E8E8F0; font-size: 15px; font-weight: bold; margin: 6px 0;">
                {titre_affiche}
            </div>
            <div style="color: #8888AA; font-size: 13px;">
                {description_affichee or ''}
            </div>
            <a href="{url_article}" target="_blank" style="color: #6C63FF; font-size: 13px;">
                Lire l'article →
            </a>
        </div>
        """, unsafe_allow_html=True)
else:
    st.error(f"Erreur : {data.get('message', 'inconnue')}")
