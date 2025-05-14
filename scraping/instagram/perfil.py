from utils.validator import extraer_emails, extraer_telefonos
from utils.normalizador import normalizar_datos_scraper
from utils.busqueda_cruzada import buscar_contacto
from services.user_agents import random_user_agent
from services.proxy_pool import ProxyPool
from services.playwright_tools import iniciar_browser_con_proxy
from services.logging_config import logger
from services.proxy_format import formatear_proxy_requests
import instaloader
from playwright.sync_api import sync_playwright


def scrapear_perfil_instagram_instaloader(username: str, forzar_solo_bio: bool = False):
	logger.info(f"📅 Intentando scrapear perfil con Instaloader: {username}")
	user_agent = random_user_agent()
	logger.info(f"🕵️ User-Agent elegido: {user_agent}")

	pool = ProxyPool()
	proxy = pool.get_random_proxy()

	if not proxy:
		logger.error("❌ No hay proxies disponibles para Instaloader.")
		return None

	logger.info(f"🧩 Proxy elegido para Instaloader: {proxy}")
	proxy_url = formatear_proxy_requests(proxy)
	insta_loader = instaloader.Instaloader(user_agent=user_agent)
	insta_loader.context._session.proxies = {
		"http": proxy_url,
		"https": proxy_url
	}

	try:
		insta_loader.load_session_from_file("pruebasrc1")
		logger.info("✅ Sesión de Instagram cargada")
	except Exception as e:
		logger.warning(f"⚠️ No se pudo cargar la sesión (no se elimina proxy): {e}")

	try:
		profile = instaloader.Profile.from_username(insta_loader.context, username)

		nombre = profile.full_name
		bio = profile.biography or ""
		hashtags = [tag.strip("#") for tag in bio.split() if tag.startswith("#")]
		emails = extraer_emails(bio)
		email = emails[0] if emails else None
		email_fuente = "bio" if email else None
		telefonos = extraer_telefonos(bio)
		telefono = telefonos[0] if telefonos else None
		seguidores = profile.followers if not forzar_solo_bio else None
		seguidos = profile.followees if not forzar_solo_bio else None
		origen = "bio" if email or telefono else "no_email"

		return normalizar_datos_scraper(nombre, username, email, email_fuente,
										telefono, seguidores, seguidos, hashtags, origen)
	except Exception as e:
		logger.error(f"❌ Error al obtener el perfil con Instaloader: {e}")
		pool.remove_proxy(proxy)
		return None


def scrapear_perfil_instagram_playwright(username: str, max_intentos: int = 1, forzar_solo_bio: bool = False):
	logger.info(f"🔍 Intentando scraping de perfil con Playwright: {username}")

	for intento in range(max_intentos):
		logger.info(f"🔁 Intento {intento + 1}/{max_intentos} para acceder al perfil...")

		try:
			# Intento con proxy
			playwright, browser, context, proxy = iniciar_browser_con_proxy("state_instagram.json")
			logger.info(f"🧩 Proxy elegido: {proxy}")
			page = context.new_page()

			try:
				logger.info("🌐 Visitando perfil en Instagram con proxy...")
				page.goto(f"https://www.instagram.com/{username}/", timeout=60000)
				page.wait_for_timeout(3000)
			except Exception as e:
				logger.error(f"❌ Fallo en navegación con proxy: {e}")
				browser.close()
				playwright.stop()

				# Fallback a IP local
				logger.warning("🔁 Reintentando con IP local...")
				try:
					playwright = sync_playwright().start()
					browser = playwright.chromium.launch(headless=True)
					context = browser.new_context(storage_state="state_instagram.json")
					page = context.new_page()
					page.goto(f"https://www.instagram.com/{username}/", timeout=60000)
					page.wait_for_timeout(3000)
				except Exception as err:
					logger.error(f"❌ Fallback con IP local también falló: {err}")
					try:
						browser.close()
						playwright.stop()
					except:
						pass
					continue

			try:
				logger.info("🔎 Extrayendo datos del perfil...")
				nombre = page.locator("header h2, header h1").first.inner_text(timeout=3000)
				bio = page.locator('meta[name="description"]').get_attribute("content") or ""
				hashtags = [tag.strip("#") for tag in bio.split() if tag.startswith("#")]
				emails = extraer_emails(bio)
				email = emails[0] if emails else None
				email_fuente = "bio" if email else None
				telefonos = extraer_telefonos(bio)
				telefono = telefonos[0] if telefonos else None
				origen = "bio" if email or telefono else "no_email"

				seguidores = None
				seguidos = None
				if not forzar_solo_bio:
					seguidores_text = page.locator("ul li:nth-child(2) span").first.get_attribute("title") or ""
					seguidos_text = page.locator("ul li:nth-child(3) span").first.inner_text() or ""
					try:
						seguidores = int(seguidores_text.replace(",", "").replace(".", ""))
					except:
						seguidores = None
					try:
						seguidos = int(seguidos_text.replace(",", "").replace(".", ""))
					except:
						seguidos = None

				logger.info("🪩 Cerrando navegador y devolviendo datos...")
				browser.close()
				playwright.stop()

				return normalizar_datos_scraper(
					nombre, username, email, email_fuente,
					telefono, seguidores, seguidos, hashtags, origen
				)

			except Exception as e:
				logger.error(f"❌ Fallo en extracción de datos: {e}")
				browser.close()
				playwright.stop()
				continue

		except Exception as e:
			logger.error(f"❌ Error general al lanzar Playwright: {e}")
			continue

	logger.error("❌ Todos los intentos fallaron. No se pudo acceder al perfil.")
	return None


def obtener_datos_perfil_instagram_con_fallback(username: str, forzar_solo_bio: bool = False,
												habilitar_busqueda_web: bool = False) -> dict:
	logger.info(f"🚀 Iniciando scraping de perfil de Instagram para: {username}")

	datos = scrapear_perfil_instagram_instaloader(username, forzar_solo_bio=forzar_solo_bio)
	if datos and (datos.get("email") or datos.get("telefono")):
		return datos

	logger.warning("⚠️ Instaloader falló o sin datos. Probando con Playwright...")
	datos = scrapear_perfil_instagram_playwright(username, forzar_solo_bio=forzar_solo_bio)
	if datos and (datos.get("email") or datos.get("telefono")):
		return datos

	if not habilitar_busqueda_web:
		logger.info("⛔ Búsqueda cruzada desactivada por configuración del usuario.")
		return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "sin_email")

	logger.warning("⚠️ Playwright también falló o no encontró datos. Lanzando búsqueda cruzada web...")
	resultado_cruzado = buscar_contacto(
		username=username,
		nombre_completo=username,
		origen_actual="instagram",
		habilitar_busqueda_web=True  # este se pasa internamente aunque ya se ha validado fuera
	)

	if resultado_cruzado:
		return normalizar_datos_scraper(
			resultado_cruzado.get("nombre") or username,
			username,
			resultado_cruzado.get("email"),
			resultado_cruzado.get("url_fuente"),
			resultado_cruzado.get("telefono"),
			None, None, [],  # otros campos vacíos
			f"búsqueda cruzada ({resultado_cruzado.get('origen')})"
		)

	return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "error")
