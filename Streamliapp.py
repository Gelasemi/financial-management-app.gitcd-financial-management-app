# streamlit_app/streamlit_app.py

# --- IMPORTS (CORRIGÉ ET COMPLET) ---
import os  # LIGNE MANQUANTE QUI PROVOQUE L'ERREUR
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Rapports de Management Financier",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
# --- FONCTION POUR APPELER LE BACKEND ---
def call_backend(endpoint, method="GET", json_payload=None):
    """Utilitaire pour appeler notre API FastAPI."""
    # La ligne suivante fonctionnait car os est maintenant importé
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000") 
    try:
        if method == "GET":
            response = requests.get(f"{backend_url}/api/{endpoint}")
        elif method == "POST":
            response = requests.post(f"{backend_url}/api/{endpoint}", json=json_payload)
        response.raise_for_status()  # Lève une exception pour les réponses 4xx/5xx
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur de connexion au backend : {e}")
        return None

# --- PAGE D'ACCUEIL ---
st.title("🎉 Bienvenue dans l'Application de Rapports Financiers !")
st.markdown("""
Utilisez le menu à gauche pour naviguer entre les différentes sections :
- **📊 Tableau de Bord** : Vue d'ensemble des KPIs et graphiques.
- **🔮 Prédictions** : Générez des prévisions financières avec le Machine Learning.
- **📈 Analyse** : Plongez en détail dans les coûts, revenus et rentabilité.
- **🏆 Benchmarking** : Comparez vos performances avec le secteur.
- **📁 Téléversement** : Uploadez et traitez vos fichiers Excel.
""")

# Afficher le statut du backend
if st.button("Vérifier la connexion au Backend"):
    status = call_backend("health")
    if status and status.get("status") == "healthy":
        st.success("✅ Le backend est accessible et fonctionnel !")
    else:
        st.error("❌ Impossible de se connecter au backend. Vérifiez qu'il est bien démarré.")
