from tasks.celery_worker import celery_app
from scraping.instagram.perfil import extraer_datos_relevantes
from scraping.instagram.seguidores import obtener_seguidores
from scraping.tiktok.perfil import scrape_tiktok

# 🧠 Servicios extra
from services import busqueda_cruzada, history
from exports.exporter import export_to_excel


@celery_app.task(queue="scraping")
def scrape_instagram(username: str):
    datos = extraer_datos_relevantes(username)

    if not datos:
        history.guardar_historial("Instagram", username, "Fallido")
        return {"error": "No se pudo obtener el perfil"}

    if not datos.get("email"):
        resultado_cruzado = busqueda_cruzada.buscar_contacto(username, datos.get("nombre"))
        if resultado_cruzado and (resultado_cruzado.get("email") or resultado_cruzado.get("telefono")):
            datos.update({
                "email": resultado_cruzado.get("email"),
                "telefono": resultado_cruzado.get("telefono"),
                "fuente_email": resultado_cruzado.get("url_fuente"),
                "origen": f"{datos.get('origen', 'no_email')} + búsqueda cruzada ({resultado_cruzado.get('origen')})"
            })

    filename = f"exports/instagram_{username}.xlsx"
    export_to_excel([datos], filename)
    history.guardar_historial("Instagram", username, "Éxito")

    return datos


@celery_app.task(queue="scraping")
def scrape_followers(username: str, max_seguidores: int = 10):
    lista = obtener_seguidores(username, max_seguidores)
    return lista


@celery_app.task(queue="scraping")
def scrape_tiktok_task(username: str):
    import asyncio
    from scraping.tiktok.perfil import scrape_tiktok
    from services import busqueda_cruzada, history
    from exports.exporter import export_to_excel

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    datos = loop.run_until_complete(scrape_tiktok(username))

    if not datos:
        history.guardar_historial("TikTok", username, "Fallido")
        return {"error": "No se pudo obtener el perfil"}

    if not datos.get("email"):
        resultado_cruzado = busqueda_cruzada.buscar_contacto(username, datos.get("nombre"))
        if resultado_cruzado and (resultado_cruzado.get("email") or resultado_cruzado.get("telefono")):
            datos.update({
                "email": resultado_cruzado.get("email"),
                "telefono": resultado_cruzado.get("telefono"),
                "fuente_email": resultado_cruzado.get("url_fuente"),
                "origen": f"{datos.get('origen', 'no_email')} + búsqueda cruzada ({resultado_cruzado.get('origen')})"
            })

    filename = f"exports/tiktok_{username}.xlsx"
    export_to_excel([datos], filename)
    history.guardar_historial("TikTok", username, "Éxito")

    return datos

