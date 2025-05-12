# ⚠️ Este script está desactivado. Solo se usa para pruebas con proxies gratuitos.

import re
import requests
from services.logging_config import logger

# Regex para validar formato IP:PUERTO
IP_PORT_REGEX = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}:\d{2,5}$")

# Fuentes de proxies HTTP gratuitos (válidas y actualizadas)
SOURCES = [
    # FUNCIONALES
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=3000&country=all&ssl=all&anonymity=all",
    "https://www.proxy-list.download/api/v1/get?type=http",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",

    # INACTIVAS (comentadas por errores recientes)
    # "https://www.proxyscan.io/api/proxy?format=txt&type=http",  # 🔴 Caída DNS – 02-may-2025
    # "https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt",  # 🔴 Error 404 – 02-may-2025
]

def is_valid_proxy(proxy: str) -> bool:
    return bool(IP_PORT_REGEX.match(proxy))

def fetch_all_proxies() -> list:
    proxies = set()
    for url in SOURCES:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                lines = response.text.splitlines()
                new_proxies = [line.strip() for line in lines if is_valid_proxy(line.strip())]
                proxies.update(new_proxies)
                logger.info(f"[Scraper] {len(new_proxies)} proxies válidos extraídos de: {url}")
            else:
                logger.warning(f"[Scraper] Error {response.status_code} en {url}")
        except Exception as e:
            logger.error(f"[Scraper] Fallo al conectar con {url}: {e}")
    logger.info(f"[Scraper] Total proxies únicos válidos: {len(proxies)}")
    return sorted(list(proxies))

def save_to_txt(proxies: list, output_file="services/raw_proxies.txt"):
    with open(output_file, "w", encoding="utf-8") as f:
        for proxy in proxies:
            f.write(proxy + "\n")
    logger.info(f"[Scraper] Proxies guardados en '{output_file}'")

if __name__ == "__main__":
    proxies = fetch_all_proxies()
    save_to_txt(proxies)
