from playwright.async_api import async_playwright
from utils.validator import extraer_emails, extraer_telefonos
from services.logging_config import logger
from utils.normalizador import normalizar_datos_scraper

async def obtener_tweets_x(username: str, max_tweets: int = 10):
    logger.info(f"✨ Iniciando scraping de tweets para: {username}")
    tweets_relevantes = []
    browser = None

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            url = f"https://twitter.com/{username}"
            logger.info(f"🌐 Navegando a: {url}")
            await page.goto(url, timeout=60000)
            await page.wait_for_timeout(4000)

            logger.info("🔄 Haciendo scroll para cargar tweets...")
            for _ in range(15):
                await page.mouse.wheel(0, 3000)
                await page.wait_for_timeout(800)

                elementos = await page.query_selector_all('article div[lang]')
                for el in elementos:
                    texto = await el.inner_text()
                    if texto not in tweets_relevantes:
                        if extraer_emails(texto) or extraer_telefonos(texto):
                            tweets_relevantes.append(texto)
                            logger.info(f"📌 Tweet relevante: {texto[:80]}...")

                    if len(tweets_relevantes) >= max_tweets:
                        break
                if len(tweets_relevantes) >= max_tweets:
                    break

    except Exception as e:
        logger.error(f"❌ Error general durante scraping de tweets: {e}")
    finally:
        if browser:
            await browser.close()

    return tweets_relevantes

async def scrape_tweets_info_x(username: str, max_tweets: int = 10):
    logger.info(f"🔍 Scrapeando tweets de X para: {username}")

    tweets = await obtener_tweets_x(username, max_tweets)
    if not tweets:
        logger.warning("⚠️ No se encontraron tweets relevantes.")
        return []

    resultados = []
    for tweet in tweets:
        emails = extraer_emails(tweet)
        telefonos = extraer_telefonos(tweet)
        email = emails[0] if emails else None
        telefono = telefonos[0] if telefonos else None
        hashtags = [palabra.strip("#") for palabra in tweet.split() if palabra.startswith("#")]

        resultado = normalizar_datos_scraper(
            nombre=username,
            usuario=username,
            email=email,
            fuente_email=f"https://twitter.com/{username}",
            telefono=telefono,
            seguidores=None,
            seguidos=None,
            hashtags=hashtags,
            origen="tweet"
        )
        resultado["tweet"] = tweet
        resultados.append(resultado)

    return resultados
