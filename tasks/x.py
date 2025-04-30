from celery_app import celery_app
from scraping.x.tweets import scrape_tweets_info_x
from services.logging_config import logger
import asyncio

@celery_app.task(name="scrape_tweets_info_x_task", queue="scraping")
def scrape_tweets_info_x_task(username: str, max_tweets: int = 10):
    logger.info(f"🚀 Tarea Celery: scrape_tweets_info_x para {username} recibida")

    try:
        datos = asyncio.run(scrape_tweets_info_x(username, max_tweets))
    except Exception as e:
        logger.error(f"❌ Error al ejecutar el scraping de tweets X: {e}")
        return {"estado": "fallo", "mensaje": f"Error en ejecución: {e}"}

    if not datos:
        logger.warning("⚠️ No se extrajo ningún tweet relevante")
        return {"estado": "fallo", "mensaje": "No se extrajo ningún tweet relevante"}

    logger.info(f"✅ Tweets relevantes extraídos correctamente para {username}")
    return {
        "estado": "ok",
        "data": datos,
        "excel_path": f"/download/tweets_x_{username}.xlsx"
    }
