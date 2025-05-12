import requests
from playwright.sync_api import sync_playwright
from services.logging_config import logger
from services.proxy_format import (
    formatear_proxy_requests,
    formatear_proxy_playwright
)

def check_proxy_requests(proxy: dict, timeout: int = 5) -> bool:
    proxy_url = formatear_proxy_requests(proxy)
    try:
        response = requests.get(
            "http://httpbin.org/ip",
            proxies={"http": proxy_url, "https": proxy_url},
            timeout=timeout
        )
        if response.status_code == 200:
            logger.info(f"[✅ Requests] Proxy válido: {proxy_url}")
            return True
    except requests.RequestException as e:
        logger.warning(f"[⚠️ Requests] Fallo con proxy {proxy_url}: {e}")
    return False

def check_proxy_playwright(proxy: dict, timeout: int = 8000) -> bool:
    proxy_config = formatear_proxy_playwright(proxy)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(proxy=proxy_config, headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto("http://httpbin.org/ip", timeout=timeout)
            logger.info(f"[✅ Playwright] Proxy válido en httpbin: {proxy_config['server']}")
            browser.close()
            return True
    except Exception as e:
        logger.error(f"[❌ Playwright] Fallo con proxy {proxy_config['server']}: {e}")
        return False

def check_proxy(proxy: dict) -> bool:
    """
    Valida un proxy dict:
    1. Con requests (httpbin)
    2. Con Playwright (httpbin)
    """
    if check_proxy_requests(proxy):
        return True
    elif check_proxy_playwright(proxy):
        return True
    else:
        logger.error(f"[⛔ Checker] Proxy inválido: {formatear_proxy_requests(proxy)}")
        return False
