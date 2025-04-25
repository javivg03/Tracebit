from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

from utils.busqueda_cruzada import buscar_contacto
from utils.validator import extraer_emails, extraer_telefonos
from services.logging_config import logger
from services.playwright_tools import iniciar_browser_con_proxy
from utils.normalizador import normalizar_datos_scraper

def obtener_datos_perfil_tiktok(username: str, forzar_solo_bio: bool = False) -> dict:
    logger.info(f"🚀 Iniciando scraping de perfil TikTok para: {username}")

    urls = [
        f"https://www.tiktok.com/@{username}",
        f"https://www.tiktok.com/search?q={quote_plus(username)}"
    ]

    resultado = None

    try:
        playwright, browser, context, proxy = iniciar_browser_con_proxy()
        logger.info(f"🧩 Proxy elegido: {proxy}")

        page = context.new_page()

        for url in urls:
            try:
                logger.info(f"🌐 Visitando: {url}")
                page.goto(url, timeout=20000)
                page.wait_for_timeout(3000)

                # Extraer bio
                try:
                    bio = page.locator('[data-e2e="user-bio"]').first.inner_text(timeout=3000)
                except PlaywrightTimeout:
                    bio = ""

                # Extraer nombre
                html = page.content()
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

                if not forzar_solo_bio:
                    # 🛠️ Aquí en el futuro podríamos intentar scrapear seguidores/seguidos
                    # Por ahora TikTok no lo permite fácil, así que lo dejamos en None
                    pass

                resultado = normalizar_datos_scraper(
                    nombre, username, email, fuente_email,
                    telefono, seguidores, seguidos, hashtags, origen
                )

                if email:
                    logger.info("✅ Email encontrado, saliendo del bucle de URLs.")
                    break

            except Exception as e:
                logger.warning(f"⚠️ Error al procesar {url}: {e}")
                continue

        browser.close()
        playwright.stop()

    except Exception as e:
        logger.error(f"❌ Error general durante scraping de TikTok: {e}")
        resultado = None

    if resultado and resultado.get("email"):
        return resultado

    return fallback_tiktok(username, resultado.get("nombre") if resultado else None)

def fallback_tiktok(username: str, nombre: str = None) -> dict:
    logger.info("🔍 Lanzando búsqueda cruzada...")
    resultado_cruzado = buscar_contacto(
        username,
        nombre_completo=nombre or username,
        origen_actual="tiktok"
    )

    if resultado_cruzado:
        return normalizar_datos_scraper(
            resultado_cruzado.get("nombre") or nombre or username,
            username,
            resultado_cruzado.get("email"),
            resultado_cruzado.get("url_fuente"),
            resultado_cruzado.get("telefono"),
            None, None, [],
            f"búsqueda cruzada ({resultado_cruzado.get('origen')})"
        )

    logger.warning("⚠️ No se encontró ningún dato en búsqueda cruzada.")
    return normalizar_datos_scraper(
        nombre, username, None, None, None, None, None, [], "error"
    )
