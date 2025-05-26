import asyncio
from celery_app import celery_app
from scraping.tiktok.seguidores import scrape_followers_info_tiktok
from scraping.tiktok.seguidos import scrape_followees_info_tiktok
from services.logging_config import logger
from exports.exporter import exportar_resultados_a_excel, exportar_resultados_a_csv
from decorators.historial import registrar_historial

@celery_app.task(name="scrape_followers_info_tiktok_task", queue="scraping")
@registrar_historial(plataforma="tiktok", tipo="seguidores")
def scrape_followers_info_tiktok_task(username: str, max_seguidores: int = 10):
    logger.info(f"🚀 Tarea Celery: scrape_followers_info_tiktok para {username} recibida")

    datos = asyncio.run(scrape_followers_info_tiktok(username, max_seguidores))

    if not datos:
        logger.warning("⚠️ No se extrajo ningún seguidor")
        return {"estado": "fallo", "mensaje": "No se extrajo ningún seguidor"}

    ruta_excel = exportar_resultados_a_excel(datos, f"seguidores_tiktok_{username}")
    ruta_csv = exportar_resultados_a_csv(datos, f"seguidores_tiktok_{username}")

    logger.info(f"✅ Seguidores de TikTok extraídos correctamente para {username}")

    return {
        "estado": "ok",
        "data": datos,
        "excel_path": ruta_excel,
        "csv_path": ruta_csv
    }


@celery_app.task(name="scrape_followees_info_tiktok_task", queue="scraping")
@registrar_historial(plataforma="tiktok", tipo="seguidos")
def scrape_followees_info_tiktok_task(username: str, max_seguidos: int = 10):
    logger.info(f"🚀 Tarea Celery: scrape_followees_info_tiktok para {username} recibida")

    datos = asyncio.run(scrape_followees_info_tiktok(username, max_seguidos))

    if not datos:
        logger.warning("⚠️ No se extrajo ningún seguido")
        return {"estado": "fallo", "mensaje": "No se extrajo ningún seguido"}

    ruta_excel = exportar_resultados_a_excel(datos, f"seguidos_tiktok_{username}")
    ruta_csv = exportar_resultados_a_csv(datos, f"seguidos_tiktok_{username}")

    logger.info(f"✅ Seguidos de TikTok extraídos correctamente para {username}")

    return {
        "estado": "ok",
        "data": datos,
        "excel_path": ruta_excel,
        "csv_path": ruta_csv
    }
