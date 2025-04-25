from starlette.concurrency import run_in_threadpool
from services.logging_config import logger
from exports.exporter import export_to_excel
from utils.history import guardar_historial

async def procesar_scraping(username: str, red: str, funcion_scraper):
    logger.info(f"🚀 Iniciando scraping de perfil {red.upper()} para: {username}")
    datos = await run_in_threadpool(funcion_scraper, username)

    if datos and datos.get("email"):
        path = f"exports/{red}_{username}.xlsx"
        export_to_excel([datos], path)
        guardar_historial(f"{red.capitalize()} - Perfil", username, "Éxito")
        logger.info(f"✅ Scraping de perfil completado para {username}, datos exportados.")
        return {"data": datos, "excel_path": f"/download/{red}_{username}.xlsx"}

    logger.warning(f"⚠️ Scraping completado pero sin email para: {username}")
    return {"data": datos, "excel_path": None}
