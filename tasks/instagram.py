import asyncio
from celery_app import celery_app
from scraping.instagram.seguidores import scrape_followers_info
from scraping.instagram.seguidos import scrape_followees_info
from services.logging_config import logger
from exports.exporter import exportar_resultados_a_excel, exportar_resultados_a_csv
from decorators.historial import registrar_historial

@celery_app.task(queue="scraping")
@registrar_historial(plataforma="instagram", tipo="seguidores")
def scrape_followers_info_task(username: str, max_seguidores: int = 3):
    logger.info(f"🚀 Tarea Celery: scrape_followers_info para {username} recibida")
    datos = asyncio.run(scrape_followers_info(username, max_seguidores))

    if not datos:
        logger.warning("⚠️ No se extrajo ningún seguidor")
        return {"estado": "fallo", "mensaje": "No se extrajo ningún seguidor"}

    ruta_excel = exportar_resultados_a_excel(datos, f"seguidores_{username}")
    ruta_csv = exportar_resultados_a_csv(datos, f"seguidores_{username}")

    return {
        "estado": "ok",
        "data": datos,
        "excel_path": ruta_excel,
        "csv_path": ruta_csv
    }

@celery_app.task(queue="scraping")
@registrar_historial(plataforma="instagram", tipo="seguidos")
def scrape_followees_info_task(username: str, max_seguidos: int = 3):
    logger.info(f"🚀 Tarea Celery: scrape_followees_info para {username} recibida")
    datos = asyncio.run(scrape_followees_info(username, max_seguidos))

    if not datos:
        logger.warning("⚠️ No se extrajo ningún seguido")
        return {"estado": "fallo", "mensaje": "No se extrajo ningún seguido"}

    ruta_excel = exportar_resultados_a_excel(datos, f"seguidos_{username}")
    ruta_csv = exportar_resultados_a_csv(datos, f"seguidos_{username}")

    return {
        "estado": "ok",
        "data": datos,
        "excel_path": ruta_excel,
        "csv_path": ruta_csv
    }
