from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Lanzamos navegador visible
    context = browser.new_context()

    page = context.new_page()
    page.goto("https://www.instagram.com/accounts/login/")

    print("🕒 Tienes 30 segundos para iniciar sesión manualmente...")
    page.wait_for_timeout(30000)  # 30 segundos para iniciar sesión manual

    # Guardar sesión ya logueada
    context.storage_state(path="state.json")
    print("✅ Sesión guardada como state.json")

    browser.close()
