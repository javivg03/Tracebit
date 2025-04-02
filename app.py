from fastapi import FastAPI, Body
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool
import traceback

from scraping.instagram.perfil import extraer_datos_relevantes
from tasks.tasks import scrape_instagram, scrape_followers
from services.history import guardar_historial
from exports.exporter import export_to_excel
import services.busqueda_cruzada as busqueda_cruzada

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

class UserInput(BaseModel):
    username: str

@app.get("/")
def root():
    return FileResponse("static/index.html")

# 🔍 Scraping directo de perfil de Instagram con búsqueda cruzada
@app.post("/scrape/instagram")
async def instagram_scraper(data: UserInput = Body(...)):
    try:
        datos = await run_in_threadpool(extraer_datos_relevantes, data.username)

        if not datos:
            raise Exception("El scraper devolvió None")

        if not datos.get("email"):
            resultado_cruzado = await run_in_threadpool(
                busqueda_cruzada.buscar_contacto, data.username, datos.get("nombre")
            )
            if resultado_cruzado and (resultado_cruzado.get("email") or resultado_cruzado.get("telefono")):
                datos.update({
                    "email": resultado_cruzado.get("email"),
                    "telefono": resultado_cruzado.get("telefono"),
                    "fuente_email": resultado_cruzado.get("url_fuente"),
                    "origen": f"{datos.get('origen', 'no_email')} + búsqueda cruzada ({resultado_cruzado.get('origen')})"
                })

        filename = f"exports/instagram_{data.username}.xlsx"
        export_to_excel([datos], filename)
        guardar_historial("Instagram", data.username, "Éxito")

        return {
            "data": datos,
            "excel_path": f"/download/instagram_{data.username}.xlsx"
        }

    except Exception as e:
        print("❌ Error en /scrape/instagram:")
        print(traceback.format_exc())
        return JSONResponse(status_code=400, content={"error": f"No se pudo scrapear Instagram: {str(e)}"})

# 🚀 Scraping de perfil en segundo plano (cola Celery)
@app.post("/scrapear/instagram/{username}")
def lanzar_scraping_perfil(username: str):
    tarea = scrape_instagram.delay(username)
    return {"mensaje": "Scraping del perfil en curso", "tarea_id": tarea.id}

# 👥 Scraping de seguidores en segundo plano (cola Celery)
@app.post("/scrapear/seguidores/{username}")
def lanzar_scraping_seguidores(username: str):
    tarea = scrape_followers.delay(username)
    return {"mensaje": "Extracción de seguidores en curso", "tarea_id": tarea.id}
