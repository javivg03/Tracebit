from playwright.sync_api import sync_playwright

def guardar_state_youtube():
    with sync_playwright() as p:
        print("🧠 Lanzando navegador para guardar sesión de YouTube...")

        browser = p.chromium.launch(headless=False, slow_mo=200)
        context = browser.new_context(
            permissions=["notifications"],
            viewport={"width": 1280, "height": 800},
            ignore_https_errors=True,
            java_script_enabled=True
        )

        context.set_default_timeout(60000)
        context.set_default_navigation_timeout(60000)

        page = context.new_page()
        print("🌐 Abriendo página de login de YouTube (Google)...")
        page.goto("https://accounts.google.com/ServiceLogin?service=youtube")

        print("\n👉 Inicia sesión con tu cuenta de Google (email, contraseña y 2FA si lo tienes activado).")
        print("🔐 Cuando completes el login, vuelve aquí y pulsa ENTER para guardar la sesión.")

        input("⏳ Esperando tu confirmación (ENTER)...")

        context.storage_state(path="state_youtube.json")
        print("✅ Sesión guardada en 'state_youtube.json' correctamente.")

        browser.close()

guardar_state_youtube()
