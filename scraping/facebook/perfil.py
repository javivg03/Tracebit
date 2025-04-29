from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from utils.validator import extraer_emails, extraer_telefonos
from utils.normalizador import normalizar_datos_scraper
from services.logging_config import logger
from utils.busqueda_cruzada import buscar_contacto


async def obtener_datos_perfil_facebook(username_o_nombre: str, forzar_solo_bio: bool = False) -> dict:
    logger.info(f"✨ Iniciando scraping de Facebook para: {username_o_nombre}")

    # Decide si buscar por username o por nombre real
    es_nombre_real = " " in username_o_nombre.strip()

    urls = []
    if es_nombre_real:
        # Buscar por nombre real
        urls.append(f"https://www.facebook.com/public?q={quote_plus(username_o_nombre)}")
    else:
        # Primero intentar como username, luego búsqueda pública
        urls.append(f"https://www.facebook.com/{username_o_nombre}")
        urls.append(f"https://www.facebook.com/public?q={quote_plus(username_o_nombre)}")

    resultado = None

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            for url in urls:
                try:
                    logger.info(f"🌐 Visitando: {url}")
                    await page.goto(url, timeout=15000)
                    await page.wait_for_timeout(3000)

                    html = await page.content()
                    soup = BeautifulSoup(html, "html.parser")
                    text = soup.get_text(separator=" ", strip=True)

                    emails = extraer_emails(text)
                    telefonos = extraer_telefonos(text)

                    if emails:
                        email_valido = emails[0]
                        telefono_valido = telefonos[0] if telefonos else None

                        resultado = normalizar_datos_scraper(
                            nombre=username_o_nombre,
                            usuario=username_o_nombre,
                            email=email_valido,
                            fuente_email=url,
                            telefono=telefono_valido,
                            seguidores=None,
                            seguidos=None,
                            hashtags=[],
                            origen="facebook"
                        )
                        break

                except Exception as e:
                    logger.warning(f"⚠️ Error procesando {url}: {e}")
                    continue

            await page.close()
            await context.close()
            await browser.close()

    except Exception as e:
        logger.error(f"❌ Error general durante scraping de Facebook: {e}")

    # Si encontramos algo útil
    if resultado and (resultado.get("email") or resultado.get("telefono")):
        return resultado

    # 🔍 Si no encontramos nada, lanzar búsqueda cruzada limitada
    logger.warning(f"⚠️ No se encontraron datos en scraping. Lanzando búsqueda cruzada...")
    resultado_cruzado = buscar_contacto(
        username=username_o_nombre,
        nombre_completo=username_o_nombre,
        origen_actual="facebook"
    )

    if resultado_cruzado:
        logger.info(f"✅ Datos encontrados en búsqueda cruzada: {resultado_cruzado}")
        return normalizar_datos_scraper(
            nombre=resultado_cruzado.get("nombre") or username_o_nombre,
            usuario=username_o_nombre,
            email=resultado_cruzado.get("email"),
            fuente_email=resultado_cruzado.get("url_fuente"),
            telefono=resultado_cruzado.get("telefono"),
            seguidores=None,
            seguidos=None,
            hashtags=[],
            origen=f"búsqueda cruzada ({resultado_cruzado.get('origen')})"
        )

    logger.warning(f"❌ No se encontró ningún dato útil para {username_o_nombre} tras scraping + búsqueda cruzada.")
    return normalizar_datos_scraper(
        nombre=None,
        usuario=username_o_nombre,
        email=None,
        fuente_email=None,
        telefono=None,
        seguidores=None,
        seguidos=None,
        hashtags=[],
        origen="error"
    )
