from services.logging_config import logger
from utils.normalizador import normalizar_datos_scraper, construir_origen
from utils.busqueda_cruzada import buscar_contacto
from decorators.historial import registrar_historial_async

from scraping.telegram.canal import obtener_datos_canal_telegram
from scraping.instagram.perfil import obtener_datos_perfil_instagram
from scraping.tiktok.perfil import obtener_datos_perfil_tiktok
from scraping.facebook.perfil import obtener_datos_perfil_facebook
from scraping.x.perfil import obtener_datos_perfil_x
from scraping.youtube.canal import obtener_datos_perfil_youtube
from utils.history import guardar_resultado_temporal

# Mapeo red → función
SCRAPERS = {
    "telegram": obtener_datos_canal_telegram,
    "instagram": obtener_datos_perfil_instagram,
    "tiktok": obtener_datos_perfil_tiktok,
    "facebook": obtener_datos_perfil_facebook,
    "x": obtener_datos_perfil_x,
    "youtube": obtener_datos_perfil_youtube,
}


@registrar_historial_async(plataforma="multired", tipo="perfil")
# 🔒 Búsqueda cruzada desactivada temporalmente
async def flujo_scraping_multired(username: str, redes: list[str], habilitar_busqueda_web: bool = False) -> dict:
    redes_visitadas = set()

    for red in redes:
        try:
            datos = await SCRAPERS[red](username, redes_visitadas=redes_visitadas)
            if datos and (datos.get("email") or datos.get("telefono")):
                resultado_normalizado = normalizar_datos_scraper(
                    nombre=datos.get("nombre"),
                    usuario=username,
                    email=datos.get("email"),
                    telefono=datos.get("telefono"),
                    origen=construir_origen(red, datos.get("email"), datos.get("telefono"))
                )
                guardar_resultado_temporal("perfil", username, resultado_normalizado)
                return resultado_normalizado
        except Exception as e:
            logger.warning(f"⚠️ Error en scraper de {red} con {username}: {e}")

    logger.info("🔚 No se encontró contacto en redes sociales.")

    # if not habilitar_busqueda_web:
    #    logger.info("⛔ Búsqueda web desactivada por configuración.")
    #    return normalizar_datos_scraper(
    #        nombre=None,
    #        usuario=username,
    #        email=None,
    #        telefono=None,
    #        origen="sin_resultado"
    #    )

    resultado = await buscar_contacto(
        username=username,
        nombre_completo=username,
        origen_actual="flujo_multired",
        habilitar_busqueda_web=True
    )

    if resultado:
        resultado_normalizado = normalizar_datos_scraper(
            nombre=resultado.get("nombre") or username,
            usuario=username,
            email=resultado.get("email"),
            telefono=resultado.get("telefono"),
            origen=f"búsqueda cruzada ({resultado.get('origen')})"
        )
        guardar_resultado_temporal("perfil", username, resultado_normalizado)
        return resultado_normalizado

    logger.warning(f"❌ No se encontró ningún dato útil para {username} tras scraping + búsqueda cruzada.")
    return normalizar_datos_scraper(
        nombre=None,
        usuario=username,
        email=None,
        telefono=None,
        origen="sin_resultado"
    )
