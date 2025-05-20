import requests
from bs4 import BeautifulSoup
from utils.validator import extraer_emails, extraer_telefonos
from utils.normalizador import normalizar_datos_scraper
from utils.busqueda_cruzada import buscar_contacto
from services.logging_config import logger

async def obtener_datos_canal_telegram(username: str, habilitar_busqueda_web: bool = False) -> dict:
    logger.info(f"✨ Iniciando scraping de canal Telegram: {username}")

    url = f"https://t.me/s/{username}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            logger.warning(f"❌ No se pudo acceder al canal ({res.status_code})")
            raise Exception(f"Status code {res.status_code}")

        soup = BeautifulSoup(res.text, "html.parser")
        title = soup.select_one(".tgme_channel_info_header_title")
        description = soup.select_one(".tgme_channel_info_description")
        subs = soup.select_one(".tgme_channel_info_counter")

        raw_text = soup.get_text(separator=" ", strip=True)

        emails = extraer_emails(raw_text)
        email = emails[0] if emails else None
        fuente_email = "canal" if email else None

        telefonos = extraer_telefonos(raw_text)
        telefono = telefonos[0] if telefonos else None

        try:
            seguidores = int(subs.text.strip().replace(" ", "").replace(".", "").replace(",", ""))
        except (AttributeError, ValueError):
            seguidores = None

        origen = "canal" if email or telefono else "no_email"

        datos = normalizar_datos_scraper(
            nombre=title.text.strip() if title else None,
            usuario=username,
            email=email,
            fuente_email=fuente_email,
            telefono=telefono,
            seguidores=seguidores,
            seguidos=None,
            hashtags=[],
            origen=origen
        )

        if email or telefono:
            return datos

        logger.warning("⚠️ Canal sin email ni teléfono. Lanzando búsqueda cruzada...")

    except Exception as e:
        logger.error(f"❌ Error al scrapear el canal: {e}")

    if not habilitar_busqueda_web:
        logger.info("⛔ Búsqueda cruzada desactivada.")
        return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "sin_email")

    resultado = await buscar_contacto(
        username=username,
        nombre_completo=username,
        origen_actual="telegram",
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
