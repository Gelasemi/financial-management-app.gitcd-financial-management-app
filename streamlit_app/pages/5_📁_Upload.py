import streamlit as st
import requests
import io

# Importer la fonction utilitaire
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from streamlit_app import call_backend

st.set_page_config(page_title="Téléversement de Fichier", page_icon="📁")

st.title("📁 Téléverser un Nouveau Rapport")

st.sidebar.header("Détails du Rapport")
uploaded_file = st.sidebar.file_uploader(
    "Choisissez un fichier Excel",
    type=['xlsx'],
    help="Téléversez votre fichier de rapport de management (format .xlsx)"
)

month = st.sidebar.text_input("Mois du rapport (ex: 2025-10)", value="2025-10")
year = st.sidebar.number_input("Année du rapport", value=2025, min_value=2020, max_value=2030)

if uploaded_file and month and year:
    # Préparer le fichier pour l'envoi
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    # Préparer les données du formulaire
    payload = {"month": month, "year": year}
    
    # Envoyer la requête multipart/form-data
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    with st.spinner("Téléversement et traitement en cours..."):
        try:
            response = requests.post(
                f"{backend_url}/api/data/upload",
                files=files,
                data=payload
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("success"):
                st.success(f"✅ Le fichier '{uploaded_file.name}' a été téléversé et traité avec succès !")
                st.info("Les données sont maintenant disponibles dans le Tableau de Bord.")
            else:
                st.error(f"❌ Erreur lors du traitement : {result.get('message', 'Erreur inconnue')}")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Erreur de communication avec le backend : {e}")
else:
    st.info("Veuillez remplir toutes les informations dans la barre latérale pour téléverser un fichier.")
