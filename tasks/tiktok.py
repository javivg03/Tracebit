import asyncio
from celery_app import celery_app
from scraping.tiktok.seguidores import scrape_followers_info_tiktok
from scraping.tiktok.seguidos import scrape_followees_info_tiktok
from services.logging_config import logger
from decorators.historial import registrar_historial
from utils.history import guardar_resultado_temporal  # ✅ NUEVO

@celery_app.task(name="scrape_followers_info_tiktok_task", queue="scraping")
@registrar_historial(plataforma="tiktok", tipo="seguidores")
def scrape_followers_info_tiktok_task(username: str, max_seguidores: int = 10):
    logger.info(f"🚀 Tarea Celery: scrape_followers_info_tiktok para {username} recibida")

    datos = asyncio.run(scrape_followers_info_tiktok(username, max_seguidores))

    if not datos:
        logger.warning("⚠️ No se extrajo ningún seguidor")
        return {"estado": "fallo", "mensaje": "No se extrajo ningún seguidor"}

    guardar_resultado_temporal("seguidores", username, datos)  # ✅ ALMACENAR EN MEMORIA

    return {
        "estado": "ok",
        "data": datos
    }

@celery_app.task(name="scrape_followees_info_tiktok_task", queue="scraping")
@registrar_historial(plataforma="tiktok", tipo="seguidos")
def scrape_followees_info_tiktok_task(username: str, max_seguidos: int = 10):
    logger.info(f"🚀 Tarea Celery: scrape_followees_info_tiktok para {username} recibida")

    datos = asyncio.run(scrape_followees_info_tiktok(username, max_seguidos))

    if not datos:
        logger.warning("⚠️ No se extrajo ningún seguido")
        return {"estado": "fallo", "mensaje": "No se extrajo ningún seguido"}

    guardar_resultado_temporal("seguidos", username, datos)  # ✅ ALMACENAR EN MEMORIA

    return {
        "estado": "ok",
        "data": datos
    }
