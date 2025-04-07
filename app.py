from fastapi import FastAPI, Body
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool
from celery.result import AsyncResult
from fastapi.encoders import jsonable_encoder
from celery_app import celery_app
import traceback

from scraping.instagram.perfil import scrapear_perfil_instagram
from tasks.tasks import scrape_followers_info_task, scrape_tiktok_task

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


class UserInput(BaseModel):
    username: str

class SeguidoresRequest(BaseModel):
    max_seguidores: int = 10


@app.get("/")
def root():
    return FileResponse("static/index.html")


# 🔍 Scraping directo de perfil de Instagram (con búsqueda cruzada y exportación)
@app.post("/scrape/instagram")
async def instagram_scraper(data: UserInput = Body(...)):
    try:
        datos = await run_in_threadpool(scrapear_perfil_instagram, data.username)

        return {
            "data": datos,
            "excel_path": f"/download/instagram_{data.username}.xlsx"
        }

    except Exception as e:
        print("❌ Error en /scrape/instagram:")
        print(traceback.format_exc())
        return JSONResponse(status_code=400, content={"error": f"No se pudo scrapear Instagram: {str(e)}"})


# 👥 Scraping completo de seguidores con búsqueda cruzada
@app.post("/scrapear/seguidores-info/{username}")
def lanzar_scraping_info_seguidores(username: str, req: SeguidoresRequest = Body(...)):
    tarea = scrape_followers_info_task.delay(username, req.max_seguidores)
    print(f"Tarea lanzada con ID: {tarea.id}, max_seguidores: {req.max_seguidores}")
    return {"mensaje": "Scraping completo de seguidores en curso", "tarea_id": tarea.id}


@app.get("/resultado-tarea/{tarea_id}")
def obtener_resultado_tarea(tarea_id: str):
    resultado = AsyncResult(tarea_id, app=celery_app)

    if not resultado.ready():
        return {"estado": "pendiente"}

    if resultado.failed():
        print(f"❌ La tarea {tarea_id} falló.")
        print("Traceback:", resultado.traceback)
        return {"estado": "error", "mensaje": "La tarea falló"}

    try:
        datos = resultado.get()
        print(f"✅ Resultado obtenido correctamente: {type(datos)}")

        return JSONResponse(content=jsonable_encoder(datos))  # aseguramos serialización
    except Exception as e:
        import traceback
        print("❌ Excepción al recuperar resultado:", e)
        print(traceback.format_exc())
        return JSONResponse(status_code=500, content={"estado": "error", "mensaje": str(e)})


# 🎵 Scraping de perfil de TikTok
@app.post("/scrapear/tiktok/{username}")
def lanzar_scraping_tiktok(username: str):
    tarea = scrape_tiktok_task.delay(username)
    return {"mensaje": "Scraping de TikTok en curso", "tarea_id": tarea.id}
