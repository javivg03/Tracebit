from playwright.async_api import async_playwright
from utils.validator import extraer_emails, extraer_telefonos
from services.logging_config import logger
from utils.normalizador import normalizar_datos_scraper
from utils.busqueda_cruzada import buscar_contacto


async def obtener_datos_perfil_youtube(username: str, forzar_solo_bio: bool = False) -> dict:
    logger.info(f"✨ Iniciando scraping de perfil YouTube para: {username}")

    url = f"https://www.youtube.com/@{username}/about"
    resultado = None

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
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
                except Exception as e:
                    logger.info(f"(i) No se encontraron cookies o error controlado: {e}")

                await page.wait_for_timeout(3000)

                # Nombre del canal
                nombre = (await page.title()).replace(" - YouTube", "").strip()

                # Descripción del canal
                try:
                    desc_elem = await page.query_selector("#description-container")
                    descripcion = await desc_elem.inner_text() if desc_elem else ""
                except Exception:
                    descripcion = ""

                # 📧 Email y ☎️ Teléfono
                emails = extraer_emails(descripcion)
                email = emails[0] if emails else None
                fuente_email = url if email else None

                telefonos = extraer_telefonos(descripcion)
                telefono = telefonos[0] if telefonos else None

                origen = "bio" if email else "no_email"

                # 🌐 Enlaces externos
                enlaces = []
                try:
                    links = await page.query_selector_all("a[href^='http']")
                    for link in links:
                        href = await link.get_attribute("href")
                        if href and "youtube.com" not in href:
                            enlaces.append(str(href))
                except Exception:
                    enlaces = []

                resultado = normalizar_datos_scraper(
                    nombre=nombre,
                    usuario=username,
                    email=email,
                    fuente_email=fuente_email,
                    telefono=telefono,
                    seguidores=None,
                    seguidos=None,
                    hashtags=[],
                    origen=origen
                )

                resultado["enlaces_web"] = enlaces

            except Exception as e:
                logger.error(f"❌ Error durante scraping de perfil YouTube: {e}")
            finally:
                await page.close()
                await context.close()
                await browser.close()

    except Exception as e:
        logger.error(f"❌ Error general en Playwright YouTube: {e}")

    # Fallback: búsqueda cruzada si no se encontró email ni teléfono
    if resultado and not resultado.get("email") and not resultado.get("telefono"):
        logger.warning("⚠️ No se encontraron datos útiles en scraping. Lanzando búsqueda cruzada...")
        resultado_cruzado = buscar_contacto(username=username, nombre_completo=resultado.get("nombre"), origen_actual="youtube")

        if resultado_cruzado:
            resultado.update({
                "email": resultado_cruzado.get("email"),
                "fuente_email": resultado_cruzado.get("url_fuente"),
                "telefono": resultado_cruzado.get("telefono"),
                "origen": f"búsqueda cruzada ({resultado_cruzado.get('origen')})"
            })
            logger.info(f"✅ Datos recuperados mediante búsqueda cruzada: {resultado_cruzado}")

    if resultado:
        return resultado

    logger.warning(f"❌ No se encontró ningún dato útil para {username}")
    return normalizar_datos_scraper(
        nombre=None,
        usuario=username,
        email=None,
        fuente_email=None,
        telefono=None,
        seguidores=None,
        seguidos=None,
        hashtags=[],
        origen="error"
    )
