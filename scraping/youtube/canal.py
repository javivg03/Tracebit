from playwright.async_api import TimeoutError as PlaywrightTimeout
from utils.validator import extraer_emails_validos, extraer_telefonos
from services.logging_config import logger
from utils.normalizador import normalizar_datos_scraper
from utils.busqueda_cruzada import buscar_contacto
from utils.busqueda_username import buscar_perfiles_por_username
from services.playwright_tools import iniciar_browser_con_proxy
from services.proxy_pool import ProxyPool

async def obtener_datos_perfil_youtube(
    username: str,
    forzar_solo_bio: bool = False,
    habilitar_busqueda_web: bool = False,
    redes_visitadas: set[str] = None
) -> dict:
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
            return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "error")

        page = await context.new_page()

        try:
            logger.info(f"🌐 Navegando a {url}")
            await page.goto(url, timeout=60000)

            try:
                await page.wait_for_timeout(3000)
                boton = await page.query_selector("button:has-text('Aceptar todo')")
                if boton and await boton.is_visible():
                    await boton.click()
                    logger.info("✅ Cookies aceptadas")
            except Exception:
                pass  # Cookies no presentes, no es problema

            await page.wait_for_timeout(3000)

            nombre = (await page.title()).replace(" - YouTube", "").strip()

            try:
                desc_elem = await page.query_selector("#description-container")
                descripcion = await desc_elem.inner_text() if desc_elem else ""
            except Exception:
                descripcion = ""

            emails = extraer_emails_validos(descripcion)
            email = emails[0] if emails else None
            fuente_email = url if email else None
            telefonos = extraer_telefonos(descripcion)
            telefono = telefonos[0] if telefonos else None
            origen = "bio" if email or telefono else "no_email"

            await page.close()
            await context.close()
            await browser.close()
            await playwright.stop()

            if email or telefono:
                return normalizar_datos_scraper(
                    nombre, username, email, fuente_email,
                    telefono, None, None, [], origen
                )

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

    except Exception as e:
        logger.error(f"❌ Error general en Playwright YouTube: {e}")

    # 🔁 Buscar en otras redes sociales
    if not email and not telefono:
        logger.info("🔁 No se encontraron datos en YouTube. Buscando en otras redes por username...")
        resultado_multired = await buscar_perfiles_por_username(username, excluir=["youtube"], redes_visitadas=redes_visitadas)
        if resultado_multired:
            return resultado_multired

    # 🔍 Búsqueda cruzada
    logger.warning("⚠️ No se encontró información útil. Evaluando búsqueda cruzada...")

    if not habilitar_busqueda_web:
        return normalizar_datos_scraper(
            nombre=nombre,
            usuario=username,
            email=None,
            fuente_email=None,
            telefono=None,
            seguidores=None,
            seguidos=None,
            hashtags=[],
            origen="sin_email"
        )

    resultado_cruzado = await buscar_contacto(
        username=username,
        nombre_completo=nombre,
        origen_actual="youtube",
        habilitar_busqueda_web=True
    )

    if resultado_cruzado:
        return normalizar_datos_scraper(
            resultado_cruzado.get("nombre") or nombre,
            username,
            resultado_cruzado.get("email"),
            resultado_cruzado.get("url_fuente"),
            resultado_cruzado.get("telefono"),
            None, None, [],
            f"búsqueda cruzada ({resultado_cruzado.get('origen')})"
        )

    return normalizar_datos_scraper(nombre, username, None, None, None, None, None, [], "sin_resultado")
