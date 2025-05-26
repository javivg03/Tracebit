import asyncio
from celery_app import celery_app
from scraping.x.tweets import scrape_tweets_info_x
from services.logging_config import logger
from exports.exporter import exportar_resultados_a_excel, exportar_resultados_a_csv
from decorators.historial import registrar_historial

@celery_app.task(name="scrape_tweets_info_x_task", queue="scraping")
@registrar_historial(plataforma="x", tipo="tweets")
def scrape_tweets_info_x_task(username: str, max_tweets: int = 10):
    logger.info(f"🚀 Tarea Celery: scrape_tweets_info_x para {username} recibida")

    datos = asyncio.run(scrape_tweets_info_x(username, max_tweets))

    if not datos:
        logger.warning("⚠️ No se extrajo ningún tweet relevante")
        return {"estado": "fallo", "mensaje": "No se extrajo ningún tweet relevante"}

    nombre_archivo = f"tweets_x_{username}"
    ruta_excel = exportar_resultados_a_excel(datos, nombre_archivo)
    ruta_csv = exportar_resultados_a_csv(datos, nombre_archivo)

    logger.info(f"✅ Tweets relevantes extraídos correctamente para {username}")

    return {
        "estado": "ok",
        "data": datos,
        "excel_path": ruta_excel,
        "csv_path": ruta_csv
    }
