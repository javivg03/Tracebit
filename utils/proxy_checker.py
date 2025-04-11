import requests
from playwright.sync_api import sync_playwright

def check_proxy_requests(proxy: str, timeout: int = 5) -> bool:
    """Valida un proxy haciendo una petición HTTP simple."""
    try:
        response = requests.get(
            "http://httpbin.org/ip",
            proxies={"http": proxy, "https": proxy},
            timeout=timeout
        )
        return response.status_code == 200
    except requests.RequestException:
        return False

def check_proxy_playwright(proxy: str, timeout: int = 8000) -> bool:
    """Valida un proxy usando Playwright (headless browser)."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(proxy={"server": proxy}, headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto("http://httpbin.org/ip", timeout=timeout)
            browser.close()
            return True
    except Exception:
        return False

def check_proxy(proxy: str) -> bool:
    """Intenta validar un proxy primero con requests, luego con Playwright si falla."""
    if check_proxy_requests(proxy):
        print(f"[Checker] Proxy válido (requests): {proxy}")
        return True
    elif check_proxy_playwright(proxy):
        print(f"[Checker] Proxy válido (playwright): {proxy}")
        return True
    else:
        print(f"[Checker] Proxy inválido: {proxy}")
        return False
