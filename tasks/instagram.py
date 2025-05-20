import asyncio
from celery_app import celery_app
from scraping.instagram.seguidores import scrape_followers_info
from scraping.instagram.seguidos import scrape_followees_info
from services.logging_config import logger


@celery_app.task(queue="scraping")
def scrape_followers_info_task(username: str, max_seguidores: int = 3):
    logger.info(f"🚀 Tarea Celery: scrape_followers_info para {username} recibida")
    datos = asyncio.run(scrape_followers_info(username, max_seguidores))

    if not datos:
        logger.warning("⚠️ No se extrajo ningún seguidor")
        return {"estado": "fallo", "mensaje": "No se extrajo ningún seguidor"}

    logger.info(f"✅ Seguidores extraídos correctamente para {username}")
    return {
        "estado": "ok",
        "data": datos,
        "excel_path": f"/download/seguidores_{username}.xlsx"
    }


@celery_app.task(queue="scraping")
def scrape_followees_info_task(username: str, max_seguidos: int = 3):
    logger.info(f"🚀 Tarea Celery: scrape_followees_info para {username} recibida")
    datos = asyncio.run(scrape_followees_info(username, max_seguidos))

    if not datos:
        logger.warning("⚠️ No se extrajo ningún seguido")
        return {"estado": "fallo", "mensaje": "No se extrajo ningún seguido"}

    logger.info(f"✅ Seguidos extraídos correctamente para {username}")
    return {
        "estado": "ok",
        "data": datos,
        "excel_path": f"/download/seguidos_{username}.xlsx"
    }
