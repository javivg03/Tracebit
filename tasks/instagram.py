from celery_app import celery_app
from scraping.instagram.seguidores import scrape_followers_info as run_scrape_followers_info
from scraping.instagram.seguidos import scrape_followees_info as run_scrape_followees_info

@celery_app.task(queue="scraping")
def scrape_followers_info_task(username: str, max_seguidores: int = 3):
    print(f"🚀 Tarea Celery: scrape_followers_info para {username} recibida")
    datos = run_scrape_followers_info(username, max_seguidores)

    if not datos:
        return {"estado": "fallo", "mensaje": "No se extrajo ningún seguidor"}

    return {
        "estado": "ok",
        "data": datos,
        "excel_path": f"/download/seguidores_{username}.xlsx"
    }


@celery_app.task(queue="scraping")
def scrape_followees_info_task(username: str, max_seguidos: int = 3):
    print(f"🚀 Tarea Celery: scrape_followees_info para {username} recibida")
    datos = run_scrape_followees_info(username, max_seguidos)

    if not datos:
        return {"estado": "fallo", "mensaje": "No se extrajo ningún seguido"}

    return {
        "estado": "ok",
        "data": datos,
        "excel_path": f"/download/seguidos_{username}.xlsx"
    }
