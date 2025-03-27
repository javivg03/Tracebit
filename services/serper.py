from googlesearch import search

def buscar_en_google(query: str, num_resultados: int = 5):
    """
    Realiza una búsqueda en Google usando googlesearch-python.
    Devuelve una lista de diccionarios con títulos y enlaces.
    """
    resultados = []

    for url in search(query, num_results=num_resultados, lang="es"):
        resultados.append({
            "title": url,         # No devuelve título real, así que usamos la URL como título
            "link": url,
            "snippet": "Resultado sin snippet (versión básica)"
        })

    return resultados
