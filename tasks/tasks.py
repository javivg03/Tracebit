from scraping.instagram.perfil import extraer_datos_relevantes
from scraping.instagram.seguidores import obtener_seguidores
from tasks.celery_worker import celery_app

@celery_app.task(queue="scraping")
def scrape_instagram(username: str):
    resultado = extraer_datos_relevantes(username)
    return resultado

@celery_app.task(queue="scraping")
def scrape_followers(username: str, max_seguidores: int = 10):
    lista = obtener_seguidores(username, max_seguidores)
    return lista

