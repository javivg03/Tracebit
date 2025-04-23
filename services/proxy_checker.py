import requests
from playwright.sync_api import sync_playwright

def check_proxy_requests(proxy: str, timeout: int = 5) -> bool:
    """Valida un proxy haciendo una petición HTTP simple con requests."""
    try:
        response = requests.get(
            "http://httpbin.org/ip",
            proxies={"http": proxy, "https": proxy},
            timeout=timeout
        )
        if response.status_code == 200:
            print(f"[✅ Requests] Proxy válido: {proxy}")
            return True
    except requests.RequestException as e:
        print(f"[⚠️ Requests] Fallo con proxy {proxy}: {e}")
    return False


def check_proxy_playwright(proxy: str, timeout: int = 8000) -> bool:
    """Valida un proxy usando Playwright (headless Chromium)."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(proxy={"server": proxy}, headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto("http://httpbin.org/ip", timeout=timeout)
            print(f"[✅ Playwright] Proxy válido: {proxy}")
            browser.close()
            return True
    except Exception as e:
        print(f"[❌ Playwright] Fallo con proxy {proxy}: {e}")
        return False


def check_proxy(proxy: str) -> bool:
    """Valida un proxy con requests y, si falla, con Playwright."""
    if check_proxy_requests(proxy):
        return True
    elif check_proxy_playwright(proxy):
        return True
    else:
        print(f"[⛔ Checker] Proxy inválido: {proxy}")
        return False
