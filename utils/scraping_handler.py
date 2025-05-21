from utils.history import guardar_historial, fue_scrapeado_recentemente
from services.logging_config import logger
from exports.exporter import export_to_excel
import asyncio
from starlette.concurrency import run_in_threadpool

async def procesar_scraping(username: str, red: str, funcion_scraper, habilitar_busqueda_web: bool = False):
    logger.info(f"🚀 Iniciando scraping de perfil {red.upper()} para: {username}")

    # Evitar scraping duplicado en menos de 24h (respetando lógica cruzada)
    if fue_scrapeado_recentemente(username, red, tipo="perfil", ventana_horas=24, requiere_cruzada=habilitar_busqueda_web):
        logger.info(f"⛔ Ya se ha scrapeado a {username} en {red} recientemente. Operación cancelada.")
        return {"data": None, "excel_path": None}

    # Ejecutar scraper
    if asyncio.iscoroutinefunction(funcion_scraper):
        datos = await funcion_scraper(username, habilitar_busqueda_web=habilitar_busqueda_web)
    else:
        datos = await run_in_threadpool(funcion_scraper, username, habilitar_busqueda_web=habilitar_busqueda_web)

    # Si se obtuvieron datos útiles
    if datos and any([datos.get("email"), datos.get("telefono"), datos.get("seguidores"), datos.get("seguidos")]):
        path = f"exports/{red}_{username}.xlsx"
        export_to_excel([datos], path)
        guardar_historial(f"{red.capitalize()} - Perfil", username, "Éxito")
        logger.info(f"✅ Scraping de perfil completado para {username}, datos exportados.")
        return {"data": datos, "excel_path": f"/download/{red}_{username}.xlsx"}

    # Si no se obtuvieron datos útiles
    resultado = "Sin datos útiles (con búsqueda cruzada)" if habilitar_busqueda_web else "Sin datos útiles"
    guardar_historial(f"{red.capitalize()} - Perfil", username, resultado)
    logger.warning(f"⚠️ Scraping completado pero sin datos relevantes para: {username}")
    return {"data": datos, "excel_path": None}
