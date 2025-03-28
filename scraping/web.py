from bs4 import BeautifulSoup
import re
import requests
from duckduckgo_search import DDGS
from services.validator import validar_email

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"


def buscar_por_keyword(keyword: str, max_results=10):
    resultados = []
    print(f"🔎 Buscando en DuckDuckGo: {keyword}")

    with DDGS() as ddgs:
        search_results = ddgs.text(keyword + " contacto email", region="es-es", safesearch="Moderate", max_results=max_results)

        for resultado in search_results:
            url = resultado.get("href") or resultado.get("url")
            if not url:
                continue
            try:
                print(f"🌐 Revisando: {url}")
                res = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
                soup = BeautifulSoup(res.text, "html.parser")
                texto = soup.get_text()
                correos = re.findall(EMAIL_REGEX, texto)
                correo_valido = next((c for c in correos if validar_email(c)), None)

                resultados.append({
                    "title": resultado.get("title", url),
                    "link": url,
                    "snippet": resultado.get("body", "Sin resumen disponible."),
                    "email": correo_valido
                })

                if len(resultados) >= max_results:
                    break

            except Exception as e:
                print(f"⚠️ Error al procesar {url}: {e}")
                continue

    return resultados