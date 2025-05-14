from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.facebook.com")

    print("➡️ Inicia sesión manualmente y presiona Enter cuando termines...")
    input()

    context.storage_state(path="state_facebook.json")
    print("✅ Sesión guardada en state_facebook.json")

    browser.close()
