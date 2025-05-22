import requests
from bs4 import BeautifulSoup
from utils.validator import extraer_emails, extraer_telefonos
from utils.normalizador import normalizar_datos_scraper
from services.logging_config import logger


async def obtener_datos_canal_telegram(
    username: str,
    redes_visitadas: set[str] = None
) -> dict | None:
    if redes_visitadas is None:
        redes_visitadas = set()
    redes_visitadas.add("telegram")

    url = f"https://t.me/s/{username}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            logger.warning(f"❌ No se pudo acceder al canal de Telegram ({res.status_code})")
            return None

        soup = BeautifulSoup(res.text, "html.parser")
        title = soup.select_one(".tgme_channel_info_header_title")
        subs = soup.select_one(".tgme_channel_info_counter")
        raw_text = soup.get_text(separator=" ", strip=True)

        emails = extraer_emails(raw_text)
        telefonos = extraer_telefonos(raw_text)

        email = emails[0] if emails else None
        telefono = telefonos[0] if telefonos else None
        fuente_email = "canal" if email else None

        try:
            seguidores = int(subs.text.strip().replace(" ", "").replace(".", "").replace(",", ""))
        except (AttributeError, ValueError):
            seguidores = None

        if email or telefono:
            logger.info(f"✅ Datos encontrados en el canal Telegram: {username}")
            return normalizar_datos_scraper(
                nombre=title.text.strip() if title else username,
                usuario=username,
                email=email,
                fuente_email=fuente_email,
                telefono=telefono,
                seguidores=seguidores,
                seguidos=None,
                hashtags=[],
                origen="canal"
            )

    except Exception as e:
        logger.error(f"❌ Error al scrapear el canal Telegram: {e}")

    logger.info(f"🔁 No se encontraron datos en Telegram para {username}")
    return None
