from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from services.playwright_tools import iniciar_browser_con_proxy
from services.logging_config import logger
from services.proxy_pool import ProxyPool
from services.proxy_format import formatear_proxy_playwright
from utils.validator import extraer_emails, extraer_telefonos
from utils.normalizador import normalizar_datos_scraper
from utils.busqueda_cruzada import buscar_contacto
import traceback

def obtener_datos_perfil_facebook(username_o_nombre: str, forzar_solo_bio: bool = False) -> dict:
    logger.info(f"✨ Iniciando scraping de Facebook para: {username_o_nombre}")

    es_nombre_real = " " in username_o_nombre.strip()
    urls = []

    if es_nombre_real:
        urls.append(f"https://www.facebook.com/public?q={quote_plus(username_o_nombre)}")
    else:
        urls.append(f"https://www.facebook.com/{username_o_nombre}")
        urls.append(f"https://www.facebook.com/public?q={quote_plus(username_o_nombre)}")

    resultado = None
    intentos_max = 5
    intentos = 0

    while intentos < intentos_max:
        try:
            playwright, browser, context, proxy = iniciar_browser_con_proxy()
            page = context.new_page()
            logger.info(f"🧩 Usando proxy: {proxy['ip']}:{proxy['port']}")

            for url in urls:
                try:
                    logger.info(f"🌐 Visitando: {url}")
                    page.goto(url, timeout=15000)
                    page.wait_for_timeout(3000)

                    html = page.content()
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
                        break  # Si encontramos datos útiles, salimos del bucle

                except Exception as e:
                    logger.warning(f"⚠️ Error procesando {url}: {e}")
                    continue

            # Cerramos navegador siempre
            try:
                page.close()
                context.close()
                browser.close()
                playwright.stop()
            except Exception as e:
                logger.warning(f"⚠️ Error al cerrar navegador: {e}")

            if resultado:
                if not resultado.get("email") and not resultado.get("telefono"):
                    logger.warning("❌ Perfil sin datos útiles, descartando...")
                    return {"error": "Perfil sin datos útiles"}
                return resultado

        except Exception as e:
            logger.warning(f"❌ Error al iniciar navegador con proxy – {e}")
            traceback.print_exc()
            intentos += 1
            continue

    # 🔍 Si no se encuentra nada, ejecutamos búsqueda cruzada
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
