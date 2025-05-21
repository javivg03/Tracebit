from playwright.async_api import TimeoutError as PlaywrightTimeout
from utils.validator import extraer_emails_validos, extraer_telefonos
from utils.normalizador import normalizar_datos_scraper
from utils.busqueda_cruzada import buscar_contacto
from utils.busqueda_username import buscar_perfiles_por_username
from services.playwright_tools import iniciar_browser_con_proxy
from services.logging_config import logger
from services.proxy_pool import ProxyPool

async def obtener_datos_perfil_x(username: str, forzar_solo_bio: bool = False, habilitar_busqueda_web: bool = False) -> dict:
    url = f"https://twitter.com/{username}"

    try:
        playwright, browser, context, proxy = await iniciar_browser_con_proxy()

        if not context:
            logger.warning("⚠️ No se pudo iniciar navegador con proxy para X.")
            return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "error")

        page = await context.new_page()

        try:
            logger.info(f"🌐 Navegando a {url}")
            await page.goto(url, timeout=60000)
            await page.wait_for_timeout(3000)

            # 🔤 Nombre del perfil
            try:
                nombre_elem = await page.query_selector('div[data-testid="UserName"] span')
                nombre = await nombre_elem.inner_text() if nombre_elem else username
            except Exception:
                nombre = username

            # 🧠 Bio del perfil
            try:
                bio_elem = await page.query_selector('div[data-testid="UserDescription"]')
                bio = await bio_elem.inner_text() if bio_elem else ""
            except Exception:
                bio = ""

            # 📧 y ☎️ en la bio
            emails = extraer_emails_validos(bio)
            email = emails[0] if emails else None
            fuente_email = url if email else None
            telefonos = extraer_telefonos(bio)
            telefono = telefonos[0] if telefonos else None
            hashtags = [tag.strip("#") for tag in bio.split() if tag.startswith("#")]
            origen = "bio" if email or telefono else "no_email"

            await page.close()
            await context.close()
            await browser.close()
            await playwright.stop()

            if email or telefono:
                return normalizar_datos_scraper(
                    nombre=nombre,
                    usuario=username,
                    email=email,
                    fuente_email=fuente_email,
                    telefono=telefono,
                    seguidores=None,
                    seguidos=None,
                    hashtags=hashtags,
                    origen=origen
                )

        except PlaywrightTimeout:
            logger.warning("❌ Timeout al cargar el perfil. Proxy marcado como bloqueado.")
            ProxyPool().reportar_bloqueo(proxy, "x")
            await browser.close()
            await playwright.stop()
            return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "timeout")

        except Exception as e:
            logger.error(f"❌ Error durante scraping de perfil X: {e}")
            await browser.close()
            await playwright.stop()

    except Exception as e:
        logger.error(f"❌ Error general en Playwright X: {e}")
        email = None
        telefono = None

    # 🔁 Si no hay email/teléfono → buscamos en otras redes
    logger.info("🔁 No se encontraron datos en X. Buscando en otras redes por username...")
    resultado_multired = await buscar_perfiles_por_username(username, excluir=["x"])
    if resultado_multired:
        return resultado_multired

    # 🔍 Búsqueda cruzada si está habilitada
    logger.warning("⚠️ No se encontró información útil. Evaluando búsqueda cruzada...")

    if not habilitar_busqueda_web:
        logger.info("⛔ Búsqueda cruzada desactivada por configuración del usuario.")
        return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "sin_email")

    resultado_cruzado = await buscar_contacto(
        username=username,
        nombre_completo=nombre if 'nombre' in locals() else username,
        origen_actual="x",
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

    return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "sin_resultado")
