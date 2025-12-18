import streamlit as st
import requests
import plotly.express as px
import pandas as pd

# Importer la fonction utilitaire du fichier parent
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from streamlit_app import call_backend

st.set_page_config(page_title="Tableau de Bord", page_icon="📊")

st.title("📊 Tableau de Bord Interactif")

# --- SÉLECTION DU MOIS ---
st.sidebar.header("Contrôles")
selected_month = st.sidebar.selectbox(
    "Sélectionner un mois",
    options=["2025-10", "2025-09", "2025-08", "2025-07", "2025-06"],
    index=0,
    help="Les données seront filtrées pour le mois sélectionné."
)

if st.sidebar.button("Rafraîchir les données"):
    st.rerun()

# --- RÉCUPÉRATION DES DONNÉES ---
data = call_backend(f"data/dashboard?month={selected_month}")

if not data or not data.get("success"):
    st.error("Impossible de charger les données du tableau de bord. Vérifiez que un rapport pour ce mois a été téléversé.")
    st.stop()

# --- AFFICHAGE DES KPIS ---
kpi = data["kpi"]
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    label="Revenu Total",
    value=f"${kpi['revenue']:,.2f}",
    delta=f"{kpi['revenueChange']:.2f}%"
)
col2.metric(
    label="Marge Brute (%)",
    value=f"{kpi['gpm']:.2f}",
    delta=f"{kpi['gpmChange']:.2f}%"
)
col3.metric(
    label="Dépenses Opérationnelles",
    value=f"${kpi['opex']:,.2f}",
    delta=f"{kpi['opexChange']:.2f}%"
)
col4.metric(
    label="Profit Net",
    value=f"${kpi['netProfit']:,.2f}",
    delta=f"{kpi['netProfitChange']:.2f}%"
)

st.divider()

# --- GRAPHIQUES ---
monthly_data = pd.DataFrame(data["monthly"])

# Graphique de l'évolution des revenus et profits
st.subheader("Évolution Mensuelle")
fig_revenue = px.line(
    monthly_data,
    x="month",
    y=["revenue", "grossProfit", "netProfit"],
    title="Revenu et Profit au fil du temps",
    labels={"revenue": "Revenu", "grossProfit": "Marge Brute", "netProfit": "Profit Net"}
)
st.plotly_chart(fig_revenue, use_container_width=True)

# Analyse par entité
st.subheader("Performance par Entité")
entity_data = pd.DataFrame(data["entities"])
fig_entities = px.bar(
    entity_data,
    x="entity",
    y="gpm",
    title="Marge Brute par Entité (%)",
    color="gpm",
    color_continuous_scale=px.colors.sequential.Viridis
)
st.plotly_chart(fig_entities, use_container_width=True)

# Tableau des Red Flags
st.subheader("🚩 Points d'Attention (Red Flags)")
red_flags = pd.DataFrame(data["redFlags"])
st.dataframe(red_flags, use_container_width=True)
