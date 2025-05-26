import requests
from bs4 import BeautifulSoup
from utils.validator import extraer_emails, extraer_telefonos
from utils.normalizador import normalizar_datos_scraper, construir_origen
from services.logging_config import logger
from services.proxy_pool import ProxyPool
from services.proxy_format import formatear_proxy_requests
from requests.exceptions import ProxyError, RequestException


async def obtener_datos_canal_telegram(
    username: str,
    redes_visitadas: set[str] = None
) -> dict | None:
    if redes_visitadas is None:
        redes_visitadas = set()
    redes_visitadas.add("telegram")

    url = f"https://t.me/s/{username}"
    headers = {"User-Agent": "Mozilla/5.0"}

    proxy = ProxyPool().get_random_proxy("telegram")
    proxies = formatear_proxy_requests(proxy)

    try:
        logger.info(f"🌐 Accediendo al canal de Telegram: {url}")
        res = requests.get(url, headers=headers, timeout=10, proxies=proxies)

        if res.status_code != 200:
            logger.warning(f"❌ No se pudo acceder al canal de Telegram ({res.status_code})")
            ProxyPool().reportar_bloqueo(proxy, "telegram")
            return None

        soup = BeautifulSoup(res.text, "html.parser")
        title = soup.select_one(".tgme_channel_info_header_title")
        raw_text = soup.get_text(separator=" ", strip=True)

        emails = extraer_emails(raw_text)
        telefonos = extraer_telefonos(raw_text)

        email = emails[0] if emails else None
        telefono = telefonos[0] if telefonos else None
        origen = construir_origen("Telegram", email, telefono)

        if email or telefono:
            logger.info(f"✅ Contacto encontrado en Telegram: {username}")
            return normalizar_datos_scraper(
                nombre=title.text.strip() if title else username,
                usuario=username,
                email=email,
                telefono=telefono,
                origen=origen
            )

    except ProxyError:
        logger.warning("❌ Proxy bloqueado por Telegram.")
        ProxyPool().reportar_bloqueo(proxy, "telegram")
    except RequestException as e:
        logger.error(f"❌ Error de red al scrapear Telegram: {e}")
    except Exception as e:
        logger.error(f"❌ Error general al scrapear el canal Telegram: {e}")

    logger.info(f"🔁 No se encontraron datos en Telegram para {username}")
    return None
