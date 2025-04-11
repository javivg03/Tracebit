from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from scraping.instagram.perfil import obtener_datos_perfil_instagram_con_fallback
from exports.exporter import export_to_excel
from services.history import guardar_historial
from utils.proxy_pool import ProxyPool

def obtener_seguidos(username: str, max_seguidos: int = 3):
    seguidos = []
    print(f"🚀 Iniciando extracción de seguidos para: {username}")

    pool = ProxyPool()
    proxy = pool.get_random_proxy()

    if not proxy:
        print("❌ No hay proxies disponibles para el navegador.")
        return []

    print(f"🧩 Proxy elegido para seguidos: {proxy}")

    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(
                    headless=True,
                    proxy={"server": proxy}
                )
            except Exception as e:
                print(f"❌ No se pudo lanzar Playwright con el proxy: {proxy}. Error: {e}")
                pool.remove_proxy(proxy)
                return []

            context = browser.new_context(storage_state="state_instagram.json")
            page = context.new_page()

            try:
                print("🌐 Accediendo al perfil...")
                page.goto(f"https://www.instagram.com/{username}/", timeout=60000)
                page.wait_for_timeout(3000)
                print("✅ Perfil cargado")

                print("🧭 Buscando botón de seguidos...")
                page.click('a[href$="/following/"]', timeout=10000)
                print("✅ Clic en botón de seguidos")
                page.wait_for_timeout(6000)

                print("🔄 Comenzando scroll y extracción de seguidos...")
                intentos_sin_nuevos = 0
                max_intentos = 12

                while len(seguidos) < max_seguidos and intentos_sin_nuevos < max_intentos:
                    page.evaluate('''() => {
                        const ul = document.querySelector('div[role="dialog"] ul');
                        if (ul && ul.parentElement) {
                            ul.parentElement.scrollTop = ul.parentElement.scrollHeight;
                        }
                    }''')
                    page.wait_for_timeout(1500)

                    items = page.evaluate('''() => {
                        const lista = [];
                        const links = document.querySelectorAll('div[role="dialog"] a[href^="/"]');
                        for (const link of links) {
                            const href = link.getAttribute("href");
                            if (href && /^\\/[^\\/]+\\/$/.test(href)) {
                                lista.push(href.replace(/\\//g, ""));
                            }
                        }
                        return lista;
                    }''')

                    nuevos = 0
                    for user in items:
                        if user not in seguidos and len(seguidos) < max_seguidos:
                            seguidos.append(user)
                            nuevos += 1
                            print(f"👤 Seguido #{len(seguidos)}: {user}")

                    if nuevos == 0:
                        intentos_sin_nuevos += 1
                        print(f"⚠️ Sin nuevos seguidos. Intento {intentos_sin_nuevos}/{max_intentos}")
                    else:
                        intentos_sin_nuevos = 0

                print(f"✅ Total de seguidos extraídos: {len(seguidos)}")

            except PlaywrightTimeout as e:
                print(f"❌ Timeout al interactuar con la página: {e}")
                pool.remove_proxy(proxy)

            except Exception as e:
                print(f"❌ Error inesperado durante el scraping: {e}")
                pool.remove_proxy(proxy)

            finally:
                print("🧹 Cerrando navegador...")
                browser.close()

    except Exception as e:
        print(f"❌ Error general en Playwright: {e}")
        pool.remove_proxy(proxy)

    return seguidos


def scrape_followees_info(username: str, max_seguidos: int = 3):
    print(f"🚀 Scraping de seguidos para: {username}")
    todos_los_datos = []

    seguidos = obtener_seguidos(username, max_seguidos=max_seguidos)

    if not seguidos:
        print("⚠️ No se encontraron seguidos.")
        return []

    for i, usuario in enumerate(seguidos):
        print(f"🔍 ({i+1}/{len(seguidos)}) Scrapeando seguido: {usuario}")
        try:
            datos = obtener_datos_perfil_instagram_con_fallback(usuario)
            todos_los_datos.append(datos)
        except Exception as e:
            print(f"❌ Error al scrapear seguido {usuario}: {e}")

    archivo_excel = f"exports/seguidos_{username}.xlsx"
    export_to_excel(todos_los_datos, archivo_excel)
    guardar_historial("Instagram - Seguidos", username, "Éxito")

    return todos_los_datos
