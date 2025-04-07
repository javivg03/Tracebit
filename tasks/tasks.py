from celery_app import celery_app

from scraping.instagram.seguidores import scrape_followers_info as run_scrape_followers_info
from scraping.tiktok.perfil import scrape_tiktok

from services import busqueda_cruzada, history
from exports.exporter import export_to_excel


@celery_app.task(queue="scraping")
def scrape_followers_info_task(username: str, max_seguidores: int = 3):
    print(f"🚀 Tarea Celery: scrape_followers_info para {username} recibida")
    datos = run_scrape_followers_info(username, max_seguidores)

    if not datos:
        return {"estado": "fallo", "mensaje": "No se extrajo ningún seguidor"}

    print(f"Datos obtenidos: {datos}")  # <-- Nuevas líneas de log

    return {
        "estado": "ok",
        "data": datos,
        "excel_path": f"/download/seguidores_{username}.xlsx"
    }



@celery_app.task(queue="scraping")
def scrape_tiktok_task(username: str):
    import asyncio

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
