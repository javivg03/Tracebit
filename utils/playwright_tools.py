from playwright.sync_api import sync_playwright

# 🔧 Versión sin proxies (temporalmente desactivados para pruebas locales)
def iniciar_browser_con_proxy(storage_state: str = None):
    """
    Lanza el navegador sin usar proxy, solo para pruebas locales.
    Devuelve playwright, browser, context, proxy=None.
    """
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=True)
    context = (
        browser.new_context(storage_state=storage_state)
        if storage_state else
        browser.new_context()
    )
    print(f"✅ Navegador lanzado SIN proxy (usando red local)")
    return playwright, browser, context, None
