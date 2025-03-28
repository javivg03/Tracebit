from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # ⬅️ headless en False para ver el navegador
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://www.youtube.com/@MrBeast/about", timeout=60000)

    print("🕐 El navegador se mantendrá abierto para inspeccionar...")
    time.sleep(1000)  # ⬅️ Mantiene abierto 1000 segundos para que inspecciones
