from services.logging_config import logger
from utils.normalizador import normalizar_datos_scraper
from utils.busqueda_cruzada import buscar_contacto

# Importa los scrapers específicos
from scraping.telegram.canal import obtener_datos_canal_telegram
from scraping.instagram.perfil import obtener_datos_perfil_instagram
from scraping.tiktok.perfil import obtener_datos_perfil_tiktok
from scraping.facebook.perfil import obtener_datos_perfil_facebook
from scraping.x.perfil import obtener_datos_perfil_x
from scraping.youtube.canal import obtener_datos_perfil_youtube


# Mapea los nombres de red a funciones scraper
SCRAPERS = {
    "telegram": obtener_datos_canal_telegram,
    "instagram": obtener_datos_perfil_instagram,
    "tiktok": obtener_datos_perfil_tiktok,
    "facebook": obtener_datos_perfil_facebook,
    "x": obtener_datos_perfil_x,
    "youtube": obtener_datos_perfil_youtube,
}


async def flujo_scraping_multired(username: str, redes: list[str], habilitar_busqueda_web: bool = False) -> dict:
    redes_visitadas = set()
    log_cruzada_mostrado = False

    for red in redes:
        logger.info(f"🌐 Probando scraping en {red} para {username}")
        try:
            datos = await SCRAPERS[red](username, redes_visitadas=redes_visitadas)

            if datos and (datos.get("email") or datos.get("telefono")):
                logger.info(f"✅ Datos encontrados en {red.capitalize()} para {username}")
                return datos
            else:
                logger.info(f"❌ Sin contacto útil en {red}")

        except Exception as e:
            logger.warning(f"⚠️ Error en {red} con {username}: {e}")

    # ⛔ No se encontró nada en las redes sociales
    if not log_cruzada_mostrado:
        logger.info("🔚 No se encontró contacto en redes sociales paralelas.")
        logger.warning("⚠️ Evaluando búsqueda cruzada...")

    if not habilitar_busqueda_web:
        logger.info("⛔ Búsqueda web desactivada por configuración.")
        return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "sin_email")

    # 🔍 Búsqueda cruzada como último recurso
    resultado = await buscar_contacto(
        username=username,
        nombre_completo=username,
        origen_actual="flujo_multired",
        habilitar_busqueda_web=True
    )

    if resultado:
        return normalizar_datos_scraper(
            nombre=resultado.get("nombre") or username,
            usuario=username,
            email=resultado.get("email"),
            fuente_email=resultado.get("url_fuente"),
            telefono=resultado.get("telefono"),
            seguidores=None,
            seguidos=None,
            hashtags=[],
            origen=f"búsqueda cruzada ({resultado.get('origen')})"
        )

    logger.warning(f"❌ No se encontró ningún dato útil para {username} tras scraping + búsqueda cruzada.")
    return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "sin_resultado")
