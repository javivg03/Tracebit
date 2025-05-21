from playwright.async_api import TimeoutError as PlaywrightTimeout
from utils.validator import extraer_emails_validos, extraer_telefonos, extraer_dominios
from services.logging_config import logger
from utils.normalizador import normalizar_datos_scraper
from utils.busqueda_cruzada import buscar_contacto, buscar_contacto_por_dominio
from services.playwright_tools import iniciar_browser_con_proxy
from services.proxy_pool import ProxyPool
from services.user_agents import random_user_agent


async def obtener_datos_perfil_youtube(username: str, forzar_solo_bio: bool = False, habilitar_busqueda_web: bool = False) -> dict:
    logger.info(f"✨ Iniciando scraping de perfil YouTube para: {username}")
    url = f"https://www.youtube.com/@{username}/about"
    resultado = None

    try:
        user_agent = random_user_agent()
        playwright, browser, context, proxy = await iniciar_browser_con_proxy()

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
            except Exception as e:
                logger.info(f"(i) No se encontraron cookies o error controlado: {e}")

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

            # Extraer enlaces externos
            enlaces = []
            try:
                links = await page.query_selector_all("a[href^='http']")
                for link in links:
                    href = await link.get_attribute("href")
                    if href and "youtube.com" not in href:
                        enlaces.append(href)
            except Exception:
                enlaces = []

            await page.close()
            await context.close()
            await browser.close()
            await playwright.stop()

            # Si se encontró contacto directo
            if email or telefono:
                resultado = normalizar_datos_scraper(
                    nombre, username, email, fuente_email,
                    telefono, None, None, [], origen
                )
                resultado["enlaces_web"] = enlaces
                return resultado

            # Scraping dirigido a dominios (bio + enlaces)
            texto_analizar = descripcion + " " + " ".join(enlaces)
            dominios = extraer_dominios(texto_analizar)

            for dominio in dominios:
                datos_dominio = await buscar_contacto_por_dominio(dominio)
                if datos_dominio:
                    resultado = normalizar_datos_scraper(
                        nombre, username,
                        datos_dominio.get("email"),
                        datos_dominio.get("url_fuente"),
                        datos_dominio.get("telefono"),
                        None, None,
                        [], "scraping_dominio"
                    )
                    resultado["enlaces_web"] = enlaces
                    return resultado

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

    # 🔍 Búsqueda cruzada si no se encontró nada
    logger.warning("⚠️ No se encontraron datos útiles. Evaluando búsqueda cruzada...")

    if not habilitar_busqueda_web:
        logger.info("⛔ Búsqueda cruzada desactivada por configuración del usuario.")
        return normalizar_datos_scraper(
            nombre=nombre if 'nombre' in locals() else None,
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
        nombre_completo=nombre if 'nombre' in locals() else username,
        origen_actual="youtube",
        habilitar_busqueda_web=True
    )

    if resultado_cruzado:
        logger.info(f"✅ Datos recuperados mediante búsqueda cruzada: {resultado_cruzado}")
        return normalizar_datos_scraper(
            resultado_cruzado.get("nombre") or nombre,
            username,
            resultado_cruzado.get("email"),
            resultado_cruzado.get("url_fuente"),
            resultado_cruzado.get("telefono"),
            None, None, [],
            f"búsqueda cruzada ({resultado_cruzado.get('origen')})"
        )

    logger.warning(f"❌ No se encontró ningún dato útil para {username}")
    return normalizar_datos_scraper(
        nombre=nombre if 'nombre' in locals() else None,
        usuario=username,
        email=None,
        fuente_email=None,
        telefono=None,
        seguidores=None,
        seguidos=None,
        hashtags=[],
        origen="sin_resultado"
    )
