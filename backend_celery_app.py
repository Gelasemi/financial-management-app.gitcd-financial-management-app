from celery import Celery
import os

# Configure Celery
app = Celery('financial_management_app')
app.config_from_object('celeryconfig')

# Set default Django settings module for celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

# Import tasks
# from app.tasks import prediction_task