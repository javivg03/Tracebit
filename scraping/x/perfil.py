from playwright.async_api import TimeoutError as PlaywrightTimeout
from utils.validator import extraer_emails_validos, extraer_telefonos
from utils.normalizador import normalizar_datos_scraper, construir_origen
from services.playwright_tools import iniciar_browser_con_proxy
from services.logging_config import logger
from services.proxy_pool import ProxyPool

async def obtener_datos_perfil_x(
    username: str,
    redes_visitadas: set[str] = None
) -> dict | None:
    if redes_visitadas is None:
        redes_visitadas = set()
    redes_visitadas.add("x")

    url = f"https://twitter.com/{username}"
    nombre = username
    email = None
    telefono = None

    try:
        playwright, browser, context, proxy = await iniciar_browser_con_proxy("state_x.json")

        if not context:
            logger.warning("⚠️ No se pudo iniciar navegador con proxy para X.")
            return None

        page = await context.new_page()

        try:
            logger.info(f"🌐 Navegando a {url}")
            await page.goto(url, timeout=60000)
            await page.wait_for_timeout(3000)

            # Nombre del perfil
            try:
                nombre_elem = await page.query_selector('div[data-testid="UserName"] span')
                nombre = await nombre_elem.inner_text() if nombre_elem else username
            except Exception:
                nombre = username

            # Bio del perfil
            try:
                bio_elem = await page.query_selector('div[data-testid="UserDescription"]')
                bio = await bio_elem.inner_text() if bio_elem else ""
            except Exception:
                bio = ""

            # Extraer email y teléfono desde bio
            emails = extraer_emails_validos(bio)
            telefonos = extraer_telefonos(bio)
            email = emails[0] if emails else None
            telefono = telefonos[0] if telefonos else None

        except PlaywrightTimeout:
            logger.warning("❌ Timeout al cargar perfil de X. Proxy marcado como bloqueado.")
            ProxyPool().reportar_bloqueo(proxy, "x")
        except Exception as e:
            logger.error(f"❌ Error durante scraping de perfil X: {e}")
        finally:
            await page.close()
            await context.close()
            await browser.close()
            await playwright.stop()

        if email or telefono:
            logger.info(f"✅ Contacto encontrado en X: {username}")
            return normalizar_datos_scraper(
                nombre=nombre,
                usuario=username,
                email=email,
                telefono=telefono,
                origen=construir_origen("x", email, telefono)
            )

    except Exception as e:
        logger.error(f"❌ Error general en Playwright X: {e}")

    logger.info(f"🔁 No se encontraron datos útiles en X para {username}")
    return None
