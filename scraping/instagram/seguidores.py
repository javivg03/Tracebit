from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from scraping.instagram.perfil import obtener_datos_perfil_instagram_con_fallback
from exports.exporter import export_to_excel
from services.history import guardar_historial


def obtener_seguidores(username: str, max_seguidores: int = 3):
    seguidores = []
    print(f"🚀 Iniciando extracción de seguidores para: {username}")

    with sync_playwright() as p:
        print("🧠 Lanzando navegador en modo headless...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state="state_instagram.json")
        page = context.new_page()

        try:
            print("🌐 Accediendo al perfil...")
            page.goto(f"https://www.instagram.com/{username}/", timeout=60000)
            page.wait_for_timeout(3000)
            print("✅ Perfil cargado")

            print("🧭 Buscando botón de seguidores...")
            page.click('a[href$="/followers/"]', timeout=10000)
            print("✅ Clic en botón de seguidores")
            page.wait_for_timeout(6000)

            print("🔄 Comenzando scroll + extracción sin esperar a visibilidad...")
            intentos_sin_nuevos = 0
            max_intentos = 12

            while len(seguidores) < max_seguidores and intentos_sin_nuevos < max_intentos:
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
                    if user not in seguidores and len(seguidores) < max_seguidores:
                        seguidores.append(user)
                        nuevos += 1
                        print(f"👤 Seguidor #{len(seguidores)}: {user}")

                if nuevos == 0:
                    intentos_sin_nuevos += 1
                    print(f"⚠️ Sin nuevos seguidores. Intento {intentos_sin_nuevos}/{max_intentos}")
                else:
                    intentos_sin_nuevos = 0

            print(f"✅ Total de seguidores extraídos: {len(seguidores)}")

        except PlaywrightTimeout as e:
            print(f"❌ Timeout al interactuar con la página: {e}")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
        finally:
            print("🧹 Cerrando navegador...")
            browser.close()

    return seguidores


def scrape_followers_info(username: str, max_seguidores: int = 3):
    print(f"🚀 Scraping de seguidores para: {username}")
    todos_los_datos = []

    seguidores = obtener_seguidores(username, max_seguidores=max_seguidores)

    if not seguidores:
        print("⚠️ No se encontraron seguidores.")
        return []

    for i, usuario in enumerate(seguidores):
        print(f"🔍 ({i+1}/{len(seguidores)}) Scrapeando seguidor: {usuario}")
        try:
            datos = obtener_datos_perfil_instagram_con_fallback(usuario)
            todos_los_datos.append(datos)
        except Exception as e:
            print(f"❌ Error al scrapear seguidor {usuario}: {e}")

    archivo_excel = f"exports/seguidores_{username}.xlsx"
    export_to_excel(todos_los_datos, archivo_excel)
    guardar_historial("Instagram - Seguidores", username, "Éxito")

    return todos_los_datos
