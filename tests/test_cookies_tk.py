from playwright.sync_api import sync_playwright

def guardar_state_tiktok():
    with sync_playwright() as p:
        print("🧠 Lanzando navegador para guardar sesión de TikTok...")
        
        browser = p.chromium.launch(headless=False, slow_mo=200)  # modo visual y lento
        context = browser.new_context(
            permissions=["notifications"],
            viewport={"width": 1280, "height": 800},
            ignore_https_errors=True,
            java_script_enabled=True
        )

        context.set_default_timeout(60000)
        context.set_default_navigation_timeout(60000)

        page = context.new_page()
        print("🌐 Abriendo página de login de TikTok...")
        page.goto("https://www.tiktok.com/login")  # Puedes cambiar a login directo por email si prefieres

        print("\n👉 Inicia sesión manualmente (Google, email, etc.) en la ventana abierta.")
        print("🔐 Cuando termines, vuelve aquí y pulsa ENTER.")

        input("⏳ Esperando tu confirmación (ENTER)...")

        # Guardar sesión en un archivo separado
        context.storage_state(path="state_tiktok.json")
        print("✅ Sesión guardada en 'state_tiktok.json' correctamente.")

        browser.close()

guardar_state_tiktok()
