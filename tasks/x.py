import asyncio
from celery_app import celery_app
from scraping.x.tweets import scrape_tweets_info_x
from services.logging_config import logger
from decorators.historial import registrar_historial
from utils.history import guardar_resultado_temporal  # ✅ Nuevo import

@celery_app.task(name="scrape_tweets_info_x_task", queue="scraping")
@registrar_historial(plataforma="x", tipo="tweets")
def scrape_tweets_info_x_task(username: str, max_tweets: int = 10):
    logger.info(f"🚀 Tarea Celery: scrape_tweets_info_x para {username} recibida")

    datos = asyncio.run(scrape_tweets_info_x(username, max_tweets))

    if not datos:
        logger.warning("⚠️ No se extrajo ningún tweet relevante")
        return {"estado": "fallo", "mensaje": "No se extrajo ningún tweet relevante"}

    guardar_resultado_temporal("tweets", username, datos)  # ✅ Guardar para exportación bajo demanda

    return {
        "estado": "ok",
        "data": datos
    }
