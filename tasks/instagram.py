import asyncio
from celery_app import celery_app
from scraping.instagram.seguidores import scrape_followers_info
from scraping.instagram.seguidos import scrape_followees_info
from services.logging_config import logger
from decorators.historial import registrar_historial
from utils.history import guardar_resultado_temporal
from exports.exporter import exportar_resultados_a_excel, exportar_resultados_a_csv
from utils.history import fue_scrapeado_recentemente

@celery_app.task(queue="scraping")
@registrar_historial(plataforma="instagram", tipo="seguidores")
def scrape_followers_info_task(username: str, max_seguidores: int = 3):
    logger.info(f"🚀 Tarea Celery: scrape_followers_info para {username} recibida")

    if fue_scrapeado_recentemente(username, plataforma="instagram", tipo="seguidores", nueva_cantidad=max_seguidores):
        logger.warning(f"⛔ Ya se ha scrapeado a {username} con >= {max_seguidores} seguidores en las últimas 24h.")
        return {
            "estado": "duplicado",
            "mensaje": f"Ya se han extraído {max_seguidores} o más seguidores recientemente para este usuario."
        }

    datos_crudos = asyncio.run(scrape_followers_info(username, max_seguidores))

    if not datos_crudos:
        logger.warning("⚠️ No se extrajo ningún seguidor")
        return {"estado": "fallo", "mensaje": "No se extrajo ningún seguidor"}

    datos_utiles = [d for d in datos_crudos if d.get("email") or d.get("telefono")]
    guardar_resultado_temporal("seguidores", username, datos_utiles)

    if not datos_utiles:
        logger.info(f"📭 Seguidores extraídos ({len(datos_crudos)}), pero sin datos de contacto")
        return {
            "estado": "sin_datos_utiles",
            "mensaje": f"{len(datos_crudos)} seguidores extraídos, pero sin datos útiles",
            "data": datos_crudos,
            "excel_path": None,
            "csv_path": None
        }

    nombre_archivo = f"tarea_{username}_seguidores"
    excel_path = exportar_resultados_a_excel(datos_utiles, nombre_archivo)
    csv_path = exportar_resultados_a_csv(datos_utiles, nombre_archivo)

    return {
        "estado": "ok",
        "mensaje": f"{len(datos_utiles)}/{len(datos_crudos)} seguidores útiles extraídos",
        "data": datos_utiles,
        "total_scrapeados": len(datos_crudos),
        "excel_path": f"/descargar/{nombre_archivo}.xlsx",
        "csv_path": f"/descargar/{nombre_archivo}.csv",
        "archivo": f"{nombre_archivo}.xlsx"
    }

@celery_app.task(queue="scraping")
@registrar_historial(plataforma="instagram", tipo="seguidos")
def scrape_followees_info_task(username: str, max_seguidos: int = 3):
    logger.info(f"🚀 Tarea Celery: scrape_followees_info para {username} recibida")

    if fue_scrapeado_recentemente(username, plataforma="instagram", tipo="seguidos", nueva_cantidad=max_seguidos):
        logger.warning(f"⛔ Ya se ha scrapeado a {username} con >= {max_seguidos} seguidos en las últimas 24h.")
        return {
            "estado": "duplicado",
            "mensaje": f"Ya se han extraído {max_seguidos} o más seguidos recientemente para este usuario."
        }

    datos_crudos = asyncio.run(scrape_followees_info(username, max_seguidos))

    if not datos_crudos:
        logger.warning("⚠️ No se extrajo ningún seguido")
        return {"estado": "fallo", "mensaje": "No se extrajo ningún seguido"}

    datos_utiles = [d for d in datos_crudos if d.get("email") or d.get("telefono")]
    guardar_resultado_temporal("seguidos", username, datos_utiles)

    if not datos_utiles:
        logger.info(f"📭 Seguidos extraídos ({len(datos_crudos)}), pero sin datos de contacto")
        return {
            "estado": "sin_datos_utiles",
            "mensaje": f"{len(datos_crudos)} seguidos extraídos, pero sin datos útiles",
            "data": datos_crudos,
            "excel_path": None,
            "csv_path": None
        }

    nombre_archivo = f"tarea_{username}_seguidos"
    excel_path = exportar_resultados_a_excel(datos_utiles, nombre_archivo)
    csv_path = exportar_resultados_a_csv(datos_utiles, nombre_archivo)

    return {
        "estado": "ok",
        "mensaje": f"{len(datos_utiles)}/{len(datos_crudos)} seguidos útiles extraídos",
        "data": datos_utiles,
        "total_scrapeados": len(datos_crudos),
        "excel_path": f"/descargar/{nombre_archivo}.xlsx",
        "csv_path": f"/descargar/{nombre_archivo}.csv",
        "archivo": f"{nombre_archivo}.xlsx"
    }


