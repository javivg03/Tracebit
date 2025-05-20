import asyncio
from starlette.concurrency import run_in_threadpool
from services.logging_config import logger
from exports.exporter import export_to_excel
from utils.history import guardar_historial
from utils.history import fue_scrapeado_recentemente

async def procesar_scraping(username: str, red: str, funcion_scraper, habilitar_busqueda_web: bool = False):
    logger.info(f"🚀 Iniciando scraping de perfil {red.upper()} para: {username}")

    # Evitar scraping duplicado en menos de 24h
    if fue_scrapeado_recentemente(username, red, tipo="perfil", ventana_horas=24):
         logger.info(f"⛔ Ya se ha scrapeado a {username} en {red} recientemente. Operación cancelada.")
         return {"data": None, "excel_path": None}

    if asyncio.iscoroutinefunction(funcion_scraper):
        datos = await funcion_scraper(username, habilitar_busqueda_web=habilitar_busqueda_web)
    else:
        datos = await run_in_threadpool(funcion_scraper, username, habilitar_busqueda_web=habilitar_busqueda_web)

    if datos and any([
        datos.get("email"),
        datos.get("telefono"),
        datos.get("seguidores"),
        datos.get("seguidos")
    ]):
        path = f"exports/{red}_{username}.xlsx"
        export_to_excel([datos], path)
        guardar_historial(f"{red.capitalize()} - Perfil", username, "Éxito")
        logger.info(f"✅ Scraping de perfil completado para {username}, datos exportados.")
        return {"data": datos, "excel_path": f"/download/{red}_{username}.xlsx"}

    guardar_historial(f"{red.capitalize()} - Perfil", username, "Sin datos útiles")
    logger.warning(f"⚠️ Scraping completado pero sin datos relevantes para: {username}")
    return {"data": datos, "excel_path": None}
