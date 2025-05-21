import logging
logger = logging.getLogger(__name__)

async def buscar_perfiles_por_username(username: str, excluir: list[str] = None, redes_visitadas: set[str] = None) -> dict:
    """
    Busca el mismo @username en otras redes sociales, evitando bucles infinitos.
    Se puede excluir redes manualmente con `excluir` o dinámicamente con `redes_visitadas`.
    """
    if excluir is None:
        excluir = []

    if redes_visitadas is None:
        redes_visitadas = set()

    try:
        from scraping.instagram.perfil import obtener_datos_perfil_instagram
        from scraping.tiktok.perfil import obtener_datos_perfil_tiktok
        from scraping.youtube.canal import obtener_datos_perfil_youtube
        from scraping.facebook.perfil import obtener_datos_perfil_facebook
        from scraping.x.perfil import obtener_datos_perfil_x
        from scraping.telegram.canal import obtener_datos_canal_telegram
    except Exception as e:
        logger.warning(f"❌ Error en lazy imports de scrapers multired: {e}")
        return None

    scrapers = [
        ("instagram", obtener_datos_perfil_instagram),
        ("tiktok", obtener_datos_perfil_tiktok),
        ("youtube", obtener_datos_perfil_youtube),
        ("facebook", obtener_datos_perfil_facebook),
        ("x", obtener_datos_perfil_x),
        ("telegram", obtener_datos_canal_telegram),
    ]

    for nombre, scraper in scrapers:
        if nombre in excluir or nombre in redes_visitadas:
            continue

        logger.info(f"🔍 Buscando en {nombre} con @{username}")
        try:
            redes_visitadas.add(nombre)
            resultado = await scraper(username, habilitar_busqueda_web=False, redes_visitadas=redes_visitadas)
            if resultado.get("email") or resultado.get("telefono"):
                logger.info(f"✅ Contacto encontrado en {nombre}")
                return resultado
        except Exception as e:
            logger.warning(f"⚠️ Error en {nombre} con {username}: {e}")

    logger.info("🔚 No se encontró contacto en redes sociales paralelas.")
    return None
