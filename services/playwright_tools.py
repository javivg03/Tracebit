from playwright.async_api import async_playwright
from services.proxy_format import formatear_proxy_playwright
from services.proxy_pool import ProxyPool
from services.logging_config import logger

# 🔁 Cambia esto cuando quieras activar/desactivar proxies
usar_proxies = False  # ← ACTIVA o DESACTIVA el uso de proxies

async def iniciar_browser_con_proxy(state_path: str = None):
    proxy = None
    proxy_config = None

    if usar_proxies:
        pool = ProxyPool()
        proxy = pool.get_random_proxy()

        if not proxy:
            logger.warning("⚠️ No hay proxies disponibles. Se usará navegador sin proxy.")
        else:
            try:
                proxy_config = formatear_proxy_playwright(proxy)
                logger.info(f"🌐 Usando proxy: {proxy_config['server']}")
            except Exception as e:
                logger.error(f"❌ Error al formatear proxy: {e}")
                proxy_config = None

    try:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(proxy=proxy_config, headless=True)

        if state_path:
            context = await browser.new_context(storage_state=state_path)
        else:
            context = await browser.new_context()

        if usar_proxies and proxy_config:
            logger.info(f"✅ Navegador lanzado CON proxy: {proxy_config['server']}")
        else:
            logger.info("✅ Navegador lanzado SIN proxy (modo IP local)")

        return playwright, browser, context, proxy

    except Exception as e:
        logger.error(f"❌ Error al lanzar navegador: {e}")
        if usar_proxies and proxy:
            ProxyPool().reportar_bloqueo(proxy, "general")
        return None, None, None, None
