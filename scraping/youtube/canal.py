from playwright.async_api import TimeoutError as PlaywrightTimeout
from utils.validator import extraer_emails_validos, extraer_telefonos
from services.logging_config import logger
from utils.normalizador import normalizar_datos_scraper, construir_origen
from services.playwright_tools import iniciar_browser_con_proxy
from services.proxy_pool import ProxyPool

async def obtener_datos_perfil_youtube(
    username: str,
    redes_visitadas: set[str] = None
) -> dict | None:
    if redes_visitadas is None:
        redes_visitadas = set()
    redes_visitadas.add("youtube")

    url = f"https://www.youtube.com/@{username}/about"
    nombre = username
    email = None
    telefono = None

    try:
        playwright, browser, context, proxy = await iniciar_browser_con_proxy("state_youtube.json")
        if not context:
            logger.warning("⚠️ No se pudo iniciar navegador con proxy para YouTube.")
            return None

        page = await context.new_page()

        try:
            logger.info(f"🌐 Navegando a {url}")
            await page.goto(url, timeout=60000)

            # Aceptar cookies si aparecen
            try:
                await page.wait_for_timeout(3000)
                boton = await page.query_selector("button:has-text('Aceptar todo')")
                if boton and await boton.is_visible():
                    await boton.click()
                    logger.info("✅ Cookies aceptadas")
            except Exception:
                pass

            await page.wait_for_timeout(3000)

            # Obtener título como nombre
            nombre = (await page.title()).replace(" - YouTube", "").strip()

            # Descripción / bio
            try:
                desc_elem = await page.query_selector("#description-container")
                descripcion = await desc_elem.inner_text() if desc_elem else ""
            except Exception:
                descripcion = ""

            emails = extraer_emails_validos(descripcion)
            email = emails[0] if emails else None
            telefonos = extraer_telefonos(descripcion)
            telefono = telefonos[0] if telefonos else None

        except PlaywrightTimeout:
            logger.warning("❌ Timeout al cargar perfil de YouTube. Proxy marcado como bloqueado.")
            ProxyPool().reportar_bloqueo(proxy, "youtube")
        except Exception as e:
            logger.error(f"❌ Error durante scraping de perfil YouTube: {e}")
        finally:
            await page.close()
            await context.close()
            await browser.close()
            await playwright.stop()

        if email or telefono:
            logger.info(f"✅ Contacto encontrado en YouTube: {username}")
            return normalizar_datos_scraper(
                nombre=nombre,
                usuario=username,
                email=email,
                telefono=telefono,
                origen=construir_origen("Youtube", email, telefono)
            )

    except Exception as e:
        logger.error(f"❌ Error general en Playwright YouTube: {e}")

    logger.info(f"🔁 No se encontraron datos útiles en YouTube para {username}")
    return None
