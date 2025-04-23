from bs4 import BeautifulSoup
import requests
import time
from duckduckgo_search import DDGS
from googlesearch import search as google_search
from utils.validator import extraer_emails, extraer_telefonos


def buscar_por_keyword(keyword: str, max_results=10):
    resultados = []
    print(f"🔎 Buscando en DuckDuckGo: {keyword}")

    search_results = None
    # Intentar obtener resultados de DuckDuckGo con reintentos
    with DDGS() as ddgs:
        max_attempts = 3
        attempt = 0
        while attempt < max_attempts:
            try:
                search_results = ddgs.text(f"{keyword} contacto email", region="es-es", safesearch="Moderate",
                                           max_results=max_results)
                break  # Se obtuvieron resultados correctamente
            except Exception as e:
                print(f"⚠️ Error en ddgs.text (Intento {attempt + 1}): {e}")
                attempt += 1
                time.sleep(3)

    # Si DuckDuckGo falla, usar Google como fallback
    if search_results is None:
        print("⚠️ No se pudieron obtener resultados de DuckDuckGo. Se intentará fallback con Google.")
        try:
            google_results = list(google_search(f"{keyword} contacto email", num_results=max_results, lang="es"))
            # Adaptar resultados de Google para que tengan una estructura similar
            search_results = []
            for url in google_results:
                search_results.append({
                    "href": url,
                    "title": "Sin título (Google)",
                    "body": ""
                })
        except Exception as e:
            raise Exception("No se pudieron obtener resultados de DuckDuckGo ni de Google.")

    # Procesar cada resultado obtenido (de DuckDuckGo o Google)
    for item in search_results:
        url = item.get("href") or item.get("url")
        titulo = item.get("title", "Sin título")
        resumen = item.get("body", "Sin resumen disponible.")
        if not url:
            continue

        max_attempts_url = 3
        for attempt_url in range(max_attempts_url):
            try:
                print(f"🌐 Accediendo a: {url} (Intento {attempt_url + 1})")
                res = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
                if res.status_code == 202:
                    print(f"⚠️ Rate limit detectado en {url} (Status: {res.status_code}). Esperando...")
                    time.sleep(3)
                    continue
                if res.status_code != 200:
                    print(f"⚠️ Código de estado {res.status_code} en {url}.")
                    break

                soup = BeautifulSoup(res.text, "html.parser")
                texto = soup.get_text(separator=" ", strip=True)

                emails = extraer_emails(texto)
                telefonos = extraer_telefonos(texto)

                if emails or telefonos:
                    resultados.append({
                        "titulo": titulo,
                        "link": url,
                        "resumen": resumen,
                        "emails": emails,
                        "telefonos": telefonos,
                        "origen": "duckduckgo" if "duckduckgo" in url else "google"
                    })
                break  # Salir del loop de intentos para esta URL
            except Exception as e:
                print(f"⚠️ Error en {url} (Intento {attempt_url + 1}): {e}")
                time.sleep(2)
                continue

        if len(resultados) >= max_results:
            break

    print(f"✅ Resultados útiles encontrados: {len(resultados)}")
    return resultados
