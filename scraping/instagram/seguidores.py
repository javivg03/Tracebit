from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

def obtener_seguidores(username: str, max_seguidores: int = 10):
    seguidores = []

    print(f"🚀 Iniciando extracción de seguidores para: {username}")

    with sync_playwright() as p:
        print("🧠 Lanzando navegador en modo headless...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state="state.json")
        page = context.new_page()

        try:
            print("🌐 Accediendo al perfil...")
            page.goto(f"https://www.instagram.com/{username}/", timeout=60000)
            page.wait_for_timeout(3000)
            print("✅ Perfil cargado")

            print("🧭 Buscando botón de seguidores...")
            page.click('a[href$="/followers/"]', timeout=10000)
            print("✅ Clic en botón de seguidores")
            page.wait_for_timeout(3000)

            print("📦 Localizando el popup de seguidores...")
            popup = page.locator('div[role="dialog"] ul')

            # Espera activa hasta que haya al menos 1 <li>
            intentos = 0
            while popup.locator('li').count() == 0 and intentos < 5:
                print(f"⏳ Esperando que se carguen seguidores... intento {intentos+1}/5")
                page.wait_for_timeout(2000)
                intentos += 1

            print("🔄 Comenzando scroll para extraer usuarios...")
            intentos_sin_nuevos = 0
            max_intentos = 5

            while len(seguidores) < max_seguidores and intentos_sin_nuevos < max_intentos:
                page.mouse.wheel(0, 2000)
                page.wait_for_timeout(1500)

                items = popup.locator('li')
                count = items.count()
                print(f"📊 Seguidores detectados hasta ahora: {count}")

                nuevos = 0
                for i in range(len(seguidores), min(count, max_seguidores)):
                    try:
                        user = items.nth(i).locator('span a').inner_text()
                        if user and user not in seguidores:
                            seguidores.append(user)
                            nuevos += 1
                            print(f"👤 Seguidor #{len(seguidores)}: {user}")
                    except:
                        continue

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
