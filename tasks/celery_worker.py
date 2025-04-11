from celery import Celery
from celery import Celery

celery_app = Celery(
    "fct_scraper",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

# Descubre todas las tareas definidas dentro del paquete tasks
celery_app.autodiscover_tasks(['tasks'])

celery_app.conf.task_routes = {
    "tasks.*": {"queue": "scraping"}
}

celery_app = Celery(
    "fct_scraper",                                # Nombre interno de la app
    broker="redis://redis:6379/0",                # Cola de tareas (Redis)
    backend="redis://redis:6379/0"                # Dónde se guardan los resultados (Redis)
)
