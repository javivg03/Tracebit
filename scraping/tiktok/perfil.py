from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

from utils.busqueda_cruzada import buscar_contacto
from utils.validator import extraer_emails, extraer_telefonos
from services.logging_config import logger
from utils.normalizador import normalizar_datos_scraper

async def obtener_datos_perfil_tiktok(username: str, forzar_solo_bio: bool = False) -> dict:
    logger.info(f"✨ Iniciando scraping async de perfil TikTok para: {username}")

    urls = [
        f"https://www.tiktok.com/@{username}",
        f"https://www.tiktok.com/search?q={quote_plus(username)}"
    ]

    resultado = None

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(storage_state="state_tiktok.json")
            page = await context.new_page()

            for url in urls:
                try:
                    logger.info(f"🌐 Visitando: {url}")
                    await page.goto(url, timeout=20000)
                    await page.wait_for_timeout(3000)

                    try:
                        bio = await page.locator('[data-e2e="user-bio"]').first.inner_text(timeout=3000)
                    except PlaywrightTimeout:
                        bio = ""

                    html = await page.content()
                    soup = BeautifulSoup(html, "html.parser")
                    nombre_tag = soup.find("h2")
                    nombre = nombre_tag.get_text(strip=True) if nombre_tag else username

                    emails = extraer_emails(bio)
                    email = emails[0] if emails else None
                    fuente_email = url if email else None
                    telefonos = extraer_telefonos(bio)
                    telefono = telefonos[0] if telefonos else None
                    hashtags = [tag.strip("#") for tag in bio.split() if tag.startswith("#")]
                    origen = "bio" if email else "no_email"

                    seguidores = None
                    seguidos = None

                    resultado = normalizar_datos_scraper(
                        nombre, username, email, fuente_email,
                        telefono, seguidores, seguidos, hashtags, origen
                    )

                    if email or telefono:
                        logger.info("✅ Email o teléfono encontrado, saliendo del bucle de URLs.")
                        break

                except Exception as e:
                    logger.warning(f"⚠️ Error al procesar {url}: {e}")
                    continue

            await context.close()
            await browser.close()

    except Exception as e:
        logger.error(f"❌ Error general durante scraping async de TikTok: {e}")
        resultado = None

    if resultado and (resultado.get("email") or resultado.get("telefono")):
        return resultado

    logger.warning("⚠️ No se encontraron datos en scraping. Lanzando búsqueda cruzada...")
    nombre_extraido = resultado.get("nombre") if resultado else username

    resultado_cruzado = buscar_contacto(
        username=username,
        nombre_completo=nombre_extraido,
        origen_actual="tiktok"
    )

    if resultado_cruzado:
        logger.info(f"✅ Datos encontrados en búsqueda cruzada: {resultado_cruzado}")
        return normalizar_datos_scraper(
            resultado_cruzado.get("nombre") or nombre_extraido,
            username,
            resultado_cruzado.get("email"),
            resultado_cruzado.get("url_fuente"),
            resultado_cruzado.get("telefono"),
            None, None, [],
            f"búsqueda cruzada ({resultado_cruzado.get('origen')})"
        )

    logger.warning(f"❌ No se encontró ningún dato útil para {username} tras scraping + búsqueda cruzada.")
    return normalizar_datos_scraper(
        None, username, None, None, None, None, None, [], "error"
    )
