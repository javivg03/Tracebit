from celery_app import celery_app
from scraping.tiktok.seguidores import scrape_followers_info_tiktok
from services.logging_config import logger
import asyncio

@celery_app.task(name="scrape_followers_info_tiktok_task", queue="scraping")
def scrape_followers_info_tiktok_task(username: str, max_seguidores: int = 10):
    logger.info(f"🚀 Tarea Celery: scrape_followers_info_tiktok para {username} recibida")

    try:
        datos = asyncio.run(scrape_followers_info_tiktok(username, max_seguidores))
    except Exception as e:
        logger.error(f"❌ Error al ejecutar el scraping de seguidores TikTok: {e}")
        return {"estado": "fallo", "mensaje": f"Error en ejecución: {e}"}

    if not datos:
        logger.warning("⚠️ No se extrajo ningún seguidor")
        return {"estado": "fallo", "mensaje": "No se extrajo ningún seguidor"}

    logger.info(f"✅ Seguidores de TikTok extraídos correctamente para {username}")
    return {
        "estado": "ok",
        "data": datos,
        "excel_path": f"/download/seguidores_tiktok_{username}.xlsx"
    }
