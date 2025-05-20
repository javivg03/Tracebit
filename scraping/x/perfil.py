from playwright.async_api import async_playwright
from utils.validator import extraer_emails, extraer_telefonos
from services.logging_config import logger
from utils.normalizador import normalizar_datos_scraper
from utils.busqueda_cruzada import buscar_contacto


async def obtener_datos_perfil_x(username: str, forzar_solo_bio: bool = False, habilitar_busqueda_web: bool = False) -> dict:
    logger.info(f"✨ Iniciando scraping de perfil X (Twitter) para: {username}")

    url = f"https://twitter.com/{username}"
    resultado = None

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                logger.info(f"🌐 Navegando a {url}")
                await page.goto(url, timeout=60000)
                await page.wait_for_timeout(3000)

                # Nombre completo del perfil
                try:
                    nombre_elem = await page.query_selector('div[data-testid="UserName"] span')
                    nombre = await nombre_elem.inner_text() if nombre_elem else username
                except Exception:
                    nombre = username

                # Bio / Descripción
                try:
                    bio_elem = await page.query_selector('div[data-testid="UserDescription"]')
                    bio = await bio_elem.inner_text() if bio_elem else ""
                except Exception:
                    bio = ""

                # 📧 Email y ☎️ Teléfono en la bio
                emails = extraer_emails(bio)
                email = emails[0] if emails else None
                fuente_email = url if email else None

                telefonos = extraer_telefonos(bio)
                telefono = telefonos[0] if telefonos else None

                hashtags = [tag.strip("#") for tag in bio.split() if tag.startswith("#")]

                origen = "bio" if email or telefono else "no_email"

                resultado = normalizar_datos_scraper(
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

            except Exception as e:
                logger.error(f"❌ Error durante scraping de perfil X: {e}")
            finally:
                await page.close()
                await context.close()
                await browser.close()

    except Exception as e:
        logger.error(f"❌ Error general en Playwright X: {e}")

    if resultado and (resultado.get("email") or resultado.get("telefono")):
        return resultado

    # 🔍 Si no se encontró nada → Búsqueda cruzada
    logger.warning(f"⚠️ No se encontró información en el perfil de {username}. Lanzando búsqueda cruzada...")

    if not habilitar_busqueda_web:
        logger.info("⛔ Búsqueda cruzada desactivada por configuración del usuario.")
        return normalizar_datos_scraper(
            nombre=resultado["nombre"] if resultado else None,
            usuario=username,
            email=None,
            fuente_email=None,
            telefono=None,
            seguidores=None,
            seguidos=None,
            hashtags=[],
            origen="sin_email"
        )

    nombre_extraido = resultado.get("nombre") if resultado else username

    resultado_cruzado = await buscar_contacto(
        username=username,
        nombre_completo=nombre_extraido,
        origen_actual="x",
        habilitar_busqueda_web=True
    )

    if resultado_cruzado:
        logger.info(f"✅ Datos encontrados en búsqueda cruzada: {resultado_cruzado}")
        return normalizar_datos_scraper(
            nombre=resultado_cruzado.get("nombre") or nombre_extraido,
            usuario=username,
            email=resultado_cruzado.get("email"),
            fuente_email=resultado_cruzado.get("url_fuente"),
            telefono=resultado_cruzado.get("telefono"),
            seguidores=None,
            seguidos=None,
            hashtags=[],
            origen=f"búsqueda cruzada ({resultado_cruzado.get('origen')})"
        )

    logger.warning(f"❌ No se encontró ningún dato útil para {username} tras scraping + búsqueda cruzada.")
    return normalizar_datos_scraper(
        nombre=resultado["nombre"] if resultado else None,
        usuario=username,
        email=None,
        fuente_email=None,
        telefono=None,
        seguidores=None,
        seguidos=None,
        hashtags=[],
        origen="sin_resultado"
    )
