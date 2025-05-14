import time
from bs4 import BeautifulSoup
from utils.validator import extraer_emails, extraer_telefonos
from services.logging_config import logger
from services.playwright_tools import iniciar_browser_con_proxy

# =========================
# FUNCIÓN AUXILIAR → Analiza una URL y extrae contacto
# =========================

def analizar_url_contacto_playwright(page, url: str, origen: str = "duckduckgo") -> dict | None:
    try:
        page.goto(url, timeout=10000)
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        texto = soup.get_text(separator=" ", strip=True)
        emails = extraer_emails(texto)
        telefonos = extraer_telefonos(texto)

        if emails or telefonos:
            return {
                "email": emails[0] if emails else None,
                "telefono": telefonos[0] if telefonos else None,
                "url_fuente": url,
                "origen": origen,
                "nombre": None
            }
    except Exception as e:
        logger.warning(f"❌ Error accediendo a {url}: {e}")
    return None

# =========================
# FUNCIÓN PRINCIPAL DE BÚSQUEDA CRUZADA
# =========================

def buscar_contacto(username: str, nombre_completo: str = None, origen_actual: str = None, habilitar_busqueda_web: bool = False) -> dict | None:
    logger.info(f"🔎 Búsqueda cruzada iniciada para {username} (origen: {origen_actual})")

    if not habilitar_busqueda_web:
        logger.info("⛔ Búsqueda web desactivada por configuración.")
        return None

    query = f'"{nombre_completo or username}" contacto OR email OR teléfono OR "sitio web"'
    intentos = 0
    max_intentos = 3

    while intentos < max_intentos:
        intentos += 1
        logger.info(f"🦆 Intento {intentos}/{max_intentos} de búsqueda DuckDuckGo para query: {query}")
        try:
            playwright, browser, context, proxy = iniciar_browser_con_proxy()
            page = context.new_page()
            page.set_default_timeout(20000)

            page.goto("https://duckduckgo.com/")
            page.wait_for_selector("input[name='q']")
            page.click("input[name='q']")
            page.keyboard.type(query, delay=100)
            page.keyboard.press("Enter")

            try:
                page.wait_for_selector("#links", timeout=20000)
            except:
                if "418" in page.url or "static-pages/418.html" in page.url:
                    logger.warning("🚫 DuckDuckGo bloqueó esta sesión (418.html). Reintentando con otro proxy...")
                    browser.close()
                    playwright.stop()
                    continue
                raise

            page.mouse.wheel(0, 500)
            page.wait_for_timeout(1500)

            soup = BeautifulSoup(page.content(), "html.parser")
            enlaces = soup.select("a.result__a, a[data-testid='result-title-a']")

            for enlace in enlaces:
                href = enlace.get("href")
                if href and href.startswith("http"):
                    logger.info(f"🔗 Analizando resultado: {href}")
                    subpage = context.new_page()
                    datos = analizar_url_contacto_playwright(subpage, href)
                    subpage.close()
                    if datos:
                        browser.close()
                        playwright.stop()
                        logger.info(f"✅ Contacto encontrado en búsqueda cruzada: {datos}")
                        return datos

            browser.close()
            playwright.stop()
            logger.info("❌ No se encontró información de contacto relevante en los resultados.")

        except Exception as e:
            logger.warning(f"❌ Error en búsqueda cruzada con Playwright: {e}")
            try:
                browser.close()
                playwright.stop()
            except:
                pass

    logger.warning("🚫 Todos los intentos fallaron para DuckDuckGo con Playwright.")
    return None

