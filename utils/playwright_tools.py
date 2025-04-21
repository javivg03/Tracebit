from playwright.sync_api import sync_playwright
from utils.proxy_pool import ProxyPool


def iniciar_browser_con_proxy(storage_state: str = None, intentos_max: int = 5):
    """
    Lanza el navegador con proxy rotativo. Si falla, prueba otro hasta que funcione o se agoten los intentos.
    Devuelve playwright, browser, context, proxy usado.
    """
    pool = ProxyPool()
    intentos = 0

    while intentos < intentos_max:
        proxy = pool.get_random_proxy()
        print(f"🔁 Intento {intentos + 1}/{intentos_max} con proxy: {proxy}")
        try:
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(
                headless=True,
                proxy={"server": proxy}
            )
            context = (
                browser.new_context(storage_state=storage_state)
                if storage_state else
                browser.new_context()
            )
            print(f"✅ Navegador lanzado con proxy: {proxy}")
            return playwright, browser, context, proxy
        except Exception as e:
            print(f"❌ Error con proxy {proxy}: {e}")
            pool.remove_proxy(proxy)
            intentos += 1

    raise Exception("❌ No se pudo lanzar el navegador con ningún proxy válido.")
