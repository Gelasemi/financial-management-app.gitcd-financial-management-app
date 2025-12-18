# ==============================================================================
# SCRIPT DE LANCEMENT POUR L'APPLICATION FINANCIÈRE (STREAMLIT)
# ==============================================================================
#
# USAGE:
#   .\run.ps1
#
# DESCRIPTION:
#   - Vérifie que Docker Desktop est en cours d'exécution.
#   - Construit et lance les services 'backend' et 'streamlit_app'.
#   - Affiche les URLs pour accéder aux applications.
#
# PRÉREQUIS:
#   - Docker Desktop pour Windows
#   - Git
#
# ==============================================================================

# Arrête le script en cas d'erreur
 $ErrorActionPreference = "Stop"

Write-Host "--- Vérification de Docker Desktop ---" -ForegroundColor Green
# Vérifie si Docker est en cours d'exécution
try {
    docker info > $null
    Write-Host "Docker Desktop est en cours d'exécution." -ForegroundColor Green
} catch {
    Write-Host "ERREUR: Docker Desktop n'est pas démarré. Veuillez le lancer avant de continuer." -ForegroundColor Red
    exit 1
}

Write-Host "--- Construction et Lancement des Conteneurs ---" -ForegroundColor Green
# Utilise 'docker compose' (avec un espace) qui est la commande moderne
docker compose up --build

Write-Host "--- Attente du démarrage des services ---" -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host "--- Vérification du statut ---" -ForegroundColor Green
docker compose ps

Write-Host ""
Write-Host "🎉 Lancement terminé !" -ForegroundColor Cyan
Write-Host "Accédez à l'application Streamlit : http://localhost:8501" -ForegroundColor White
Write-Host "Accédez à l'API Backend      : http://localhost:8000" -ForegroundColor White
Write-Host "Accédez à la documentation de l'API : http://localhost:8000/docs" -ForegroundColor White
