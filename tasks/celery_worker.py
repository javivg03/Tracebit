from celery import Celery
from tasks import tasks
celery_app = Celery(
    "fct_scraper",                                # Nombre interno de la app
    broker="redis://redis:6379/0",                # Cola de tareas (Redis)
    backend="redis://redis:6379/0"                # Dónde se guardan los resultados (Redis)
)
