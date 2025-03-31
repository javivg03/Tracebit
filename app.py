from fastapi import FastAPI, Body
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import pandas as pd

from scraping.instagram import extraer_datos_relevantes
from scraping.telegram import scrape_telegram
from scraping.youtube import scrape_youtube
from scraping.facebook import scrape_facebook
from scraping.tiktok import scrape_tiktok
from scraping.x import scrape_x
from scraping.web import buscar_por_keyword
from services.history import guardar_historial
from exports.exporter import export_to_excel

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

class UserInput(BaseModel):
    username: str

@app.get("/")
def root():
    return FileResponse("static/index.html")

# ====== FUNCIÓN REUTILIZABLE CON BÚSQUEDA CRUZADA ======

def procesar_scraper(nombre: str, username: str, funcion_scraper):
    try:
        datos = funcion_scraper(username)

        if not datos:
            raise Exception("El scraper no devolvió resultados")

        # Si no se encontró email, activar búsqueda cruzada
        if not datos.get("email"):
            from services.busqueda_cruzada import buscar_email  # Import dinámico
            resultado = buscar_email(username, datos.get("nombre"))
            datos.update({
                "email": resultado["email"],
                "fuente_email": resultado["url_fuente"],
                "origen": resultado["origen"]
            })

        filename = f"exports/{nombre.lower()}_{username}.xlsx"
        export_to_excel([datos], filename)
        guardar_historial(nombre, username, "Éxito")
        return {
            "data": datos,
            "excel_path": f"/download/{nombre.lower()}_{username}.xlsx"
        }

    except Exception as e:
        guardar_historial(nombre, username, f"Error: {str(e)}")
        return JSONResponse(status_code=400, content={"error": f"No se pudo scrapear {nombre}: {str(e)}"})

# ============ ENDPOINTS DE SCRAPING ==============

@app.post("/scrape/instagram")
def instagram_scraper(data: UserInput = Body(...)):
    return procesar_scraper("Instagram", data.username, extraer_datos_relevantes)

@app.post("/scrape/telegram")
def telegram_scraper(data: UserInput = Body(...)):
    return procesar_scraper("Telegram", data.username, scrape_telegram)

@app.post("/scrape/youtube")
def youtube_scraper(data: UserInput = Body(...)):
    return procesar_scraper("YouTube", data.username, scrape_youtube)

@app.post("/scrape/facebook")
def facebook_scraper(data: UserInput = Body(...)):
    return procesar_scraper("Facebook", data.username, scrape_facebook)

@app.post("/scrape/tiktok")
def tiktok_scraper(data: UserInput = Body(...)):
    return procesar_scraper("TikTok", data.username, scrape_tiktok)

@app.post("/scrape/x")
def x_scraper(data: UserInput = Body(...)):
    return procesar_scraper("X", data.username, scrape_x)

@app.post("/scrape/web")
def web_scraper(data: UserInput = Body(...)):
    username = data.username
    try:
        resultados = buscar_por_keyword(username)
        filename = f"exports/web_{username.replace(' ', '_')}.xlsx"
        export_to_excel(resultados, filename)
        guardar_historial("Web", username, "Éxito")
        return {"data": resultados, "excel_path": f"/download/web_{username.replace(' ', '_')}.xlsx"}
    except Exception as e:
        guardar_historial("Web", username, f"Error: {str(e)}")
        return JSONResponse(status_code=400, content={"error": str(e)})
