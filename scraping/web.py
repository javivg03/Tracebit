from bs4 import BeautifulSoup
import requests
from duckduckgo_search import DDGS

from services.validator import extraer_emails, extraer_telefonos

def buscar_por_keyword(keyword: str, max_results=10):
    resultados = []
    print(f"🔎 Buscando en DuckDuckGo: {keyword}")

    with DDGS() as ddgs:
        search_results = ddgs.text(f"{keyword} contacto email", region="es-es", safesearch="Moderate", max_results=max_results)

        for item in search_results:
            url = item.get("href") or item.get("url")
            titulo = item.get("title", "Sin título")
            resumen = item.get("body", "Sin resumen disponible.")

            if not url:
                continue

            try:
                print(f"🌐 Accediendo a: {url}")
                res = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
                if res.status_code != 200:
                    continue

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
                        "origen": "duckduckgo"
                    })

                if len(resultados) >= max_results:
                    break

            except Exception as e:
                print(f"⚠️ Error en {url}: {e}")
                continue

    print(f"✅ Resultados útiles encontrados: {len(resultados)}")
    return resultados
