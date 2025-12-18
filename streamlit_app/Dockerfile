FROM python:3.9-slim

WORKDIR /app

# Copier les dépendances et les installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Exposer le port par défaut de Streamlit
EXPOSE 8501

# Commande pour lancer l'application Streamlit
# --server.address 0.0.0.0 la rend accessible depuis l'extérieur du conteneur
CMD ["streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0"]
