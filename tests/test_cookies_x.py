from playwright.sync_api import sync_playwright

def guardar_state_x():
    with sync_playwright() as p:
        print("🧠 Lanzando navegador para guardar sesión de X (Twitter)...")

        browser = p.chromium.launch(headless=False, slow_mo=200)  # Modo visual + pausado
        context = browser.new_context(
            permissions=["notifications"],
            viewport={"width": 1280, "height": 800},
            ignore_https_errors=True,
            java_script_enabled=True
        )

        context.set_default_timeout(60000)
        context.set_default_navigation_timeout(60000)

        page = context.new_page()
        print("🌐 Abriendo página de login de X (Twitter)...")
        page.goto("https://twitter.com/login")

        print("\n👉 Inicia sesión manualmente (email/usuario + contraseña + 2FA si aplica).")
        print("🔐 Cuando termines, vuelve aquí y pulsa ENTER para guardar la sesión.")

        input("⏳ Esperando tu confirmación (ENTER)...")

        context.storage_state(path="state_x.json")
        print("✅ Sesión guardada en 'state_x.json' correctamente.")

        browser.close()

guardar_state_x()
