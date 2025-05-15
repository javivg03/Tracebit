from playwright.async_api import async_playwright
from services.proxy_format import formatear_proxy_playwright
from services.proxy_pool import ProxyPool
from services.logging_config import logger

async def iniciar_browser_con_proxy(state_path: str = None):
    pool = ProxyPool()
    proxy = pool.get_random_proxy()

    if not proxy:
        logger.error("❌ No hay proxies disponibles.")
        return None, None, None, None

    try:
        proxy_config = formatear_proxy_playwright(proxy)
        logger.info(f"🌐 Intentando lanzar navegador con proxy: {proxy_config['server']}")

        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(proxy=proxy_config, headless=True)

        if state_path:
            context = await browser.new_context(storage_state=state_path)
        else:
            context = await browser.new_context()

        logger.info(f"✅ Navegador lanzado con proxy: {proxy_config['server']}")
        return playwright, browser, context, proxy

    except Exception as e:
        logger.warning(f"❌ Error al lanzar navegador con proxy {proxy['ip']}:{proxy['port']}: {e}")
        pool.reportar_bloqueo(proxy, "duckduckgo")
        return None, None, None, None
