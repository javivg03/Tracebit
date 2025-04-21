from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from scraping.tiktok.perfil import obtener_datos_perfil_tiktok
from utils.proxy_pool import ProxyPool


async def obtener_seguidores_tiktok(username: str, max_seguidores: int = 3):
    seguidores = []
    print(f"🚀 Iniciando extracción de seguidores TikTok para: {username}")

    pool = ProxyPool()
    proxy = pool.get_random_proxy()

    if not proxy:
        print("❌ No hay proxies disponibles.")
        return []

    print(f"🧩 Proxy elegido: {proxy}")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, proxy={"server": proxy})
            context = await browser.new_context()
            page = await context.new_page()

            try:
                print("🌐 Abriendo perfil del usuario...")
                await page.goto(f"https://www.tiktok.com/@{username}/followers", timeout=20000)
                await page.wait_for_timeout(3000)

                print("🔄 Scroll y recolección de seguidores...")
                for _ in range(10):
                    await page.mouse.wheel(0, 5000)
                    await page.wait_for_timeout(1000)

                    items = await page.eval_on_selector_all(
                        'a[href^="/@"]',
                        "elements => [...new Set(elements.map(e => e.href.split('/@')[1]))]"
                    )

                    for user in items:
                        if user not in seguidores and len(seguidores) < max_seguidores:
                            seguidores.append(user)
                            print(f"👤 Seguidor #{len(seguidores)}: {user}")

                    if len(seguidores) >= max_seguidores:
                        break

            except Exception as e:
                print(f"❌ Error al navegar o extraer seguidores: {e}")
                pool.remove_proxy(proxy)

            finally:
                print("🧹 Cerrando navegador...")
                try:
                    await context.close()
                    await browser.close()
                except Exception as e:
                    print(f"⚠️ Error al cerrar navegador: {e}")

    except Exception as e:
        print(f"❌ Error general durante Playwright: {e}")
        pool.remove_proxy(proxy)

    return seguidores


async def scrape_followers_info_tiktok(username: str, max_seguidores: int = 3):
    print(f"🔍 Scrapeando seguidores de TikTok para: {username}")
    todos_los_datos = []

    seguidores = await obtener_seguidores_tiktok(username, max_seguidores=max_seguidores)
    if not seguidores:
        print("⚠️ No se encontraron seguidores.")
        return []

    for i, usuario in enumerate(seguidores):
        print(f"🔍 ({i+1}/{len(seguidores)}) Scrapeando seguidor: {usuario}")
        try:
            datos = await obtener_datos_perfil_tiktok(usuario)
            todos_los_datos.append(datos)
        except Exception as e:
            print(f"❌ Error al scrapear seguidor {usuario}: {e}")

    return todos_los_datos
