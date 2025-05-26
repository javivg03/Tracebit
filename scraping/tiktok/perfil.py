from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from playwright.async_api import TimeoutError as PlaywrightTimeout
from utils.validator import extraer_emails_validos, extraer_telefonos
from utils.normalizador import normalizar_datos_scraper, construir_origen
from services.logging_config import logger
from services.playwright_tools import iniciar_browser_con_proxy
from services.proxy_pool import ProxyPool
from services.user_agents import random_user_agent

async def obtener_datos_perfil_tiktok(
    username: str,
    redes_visitadas: set[str] = None
) -> dict | None:
    if redes_visitadas is None:
        redes_visitadas = set()
    redes_visitadas.add("tiktok")

    urls = [
        f"https://www.tiktok.com/@{username}",
        f"https://www.tiktok.com/search?q={quote_plus(username)}"
    ]

    nombre = username
    email = None
    telefono = None

    try:
        user_agent = random_user_agent()
        playwright, browser, context, proxy = await iniciar_browser_con_proxy("state_tiktok.json")

        if not context:
            logger.warning("⚠️ No se pudo iniciar navegador con proxy para TikTok.")
            return None

        page = await context.new_page()

        for url in urls:
            try:
                logger.info(f"🌐 Visitando: {url}")
                await page.goto(url, timeout=20000)
                await page.wait_for_timeout(3000)

                try:
                    bio = await page.locator('[data-e2e="user-bio"]').first.inner_text(timeout=3000)
                except:
                    bio = ""

                html = await page.content()
                soup = BeautifulSoup(html, "html.parser")
                nombre_tag = soup.find("h2")
                nombre = nombre_tag.get_text(strip=True) if nombre_tag else username

                emails = extraer_emails_validos(bio)
                email = emails[0] if emails else None

                telefonos = extraer_telefonos(bio)
                telefono = telefonos[0] if telefonos else None

                if email or telefono:
                    break

            except Exception as e:
                logger.warning(f"⚠️ Error al procesar {url}: {e}")
                continue

        await page.close()
        await context.close()
        await browser.close()
        await playwright.stop()

        if email or telefono:
            origen = construir_origen("TikTok", email, telefono)
            logger.info("✅ Contacto encontrado en TikTok:")
            return normalizar_datos_scraper(
                nombre=nombre,
                usuario=username,
                email=email,
                telefono=telefono,
                origen=origen
            )

    except PlaywrightTimeout:
        logger.warning("❌ Timeout al cargar TikTok. Proxy marcado como bloqueado.")
        ProxyPool().reportar_bloqueo(proxy, "tiktok")
    except Exception as e:
        logger.error(f"❌ Error general durante el scraping de TikTok: {e}")

    logger.info(f"🔁 No se encontraron datos útiles en TikTok para {username}")
    return None
