import requests
from services.logging_config import logger

SOURCES = [
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=3000&country=all&ssl=all&anonymity=all",
    "https://www.proxy-list.download/api/v1/get?type=http",
    "https://www.proxyscan.io/api/proxy?format=txt&type=http",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt"
]

def fetch_all_proxies() -> list:
    proxies = set()
    for url in SOURCES:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                new_proxies = [line.strip() for line in response.text.splitlines() if line.strip()]
                proxies.update(new_proxies)
                logger.info(f"[Scraper] {len(new_proxies)} proxies de: {url}")
            else:
                logger.warning(f"[Scraper] Error {response.status_code} en {url}")
        except Exception as e:
            logger.error(f"[Scraper] Fallo al conectar con {url}: {e}")
    logger.info(f"[Scraper] Total proxies únicos obtenidos: {len(proxies)}")
    return sorted(list(proxies))


def save_to_txt(proxies: list, output_file="services/raw_proxies.txt"):
    with open(output_file, "w", encoding="utf-8") as f:
        for proxy in proxies:
            f.write(proxy + "\n")
    logger.info(f"[Scraper] Proxies guardados en '{output_file}'")


if __name__ == "__main__":
    proxies = fetch_all_proxies()
    save_to_txt(proxies)
