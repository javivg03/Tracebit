from playwright.sync_api import sync_playwright
from services.proxy_pool import ProxyPool
from services.logging_config import logger

def iniciar_browser_con_proxy(storage_state: str = None, intentos_max: int = 0):
    """
    Versión forzada a usar solo IP local, sin proxies (desarrollo).
    """
    logger.warning("🚫 Rotación de proxies desactivada. Usando IP local (sin proxy)...")

    try:
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=True)
        context = (
            browser.new_context(storage_state=storage_state)
            if storage_state else
            browser.new_context()
        )
        logger.info("✅ Navegador lanzado SIN proxy (IP local)")
        return playwright, browser, context, None
    except Exception as e:
        logger.error(f"❌ Error al lanzar navegador sin proxy: {e}")
        raise Exception("❌ No se pudo lanzar el navegador con IP local.")