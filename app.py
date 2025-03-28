import csv
import os
import requests
import re
import pandas as pd
from fastapi import FastAPI, Body
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from scraping.web import buscar_por_keyword
from scraping.instagram import extraer_datos_relevantes
from exports.exporter import export_to_excel
from services.history import guardar_historial
from scraping.telegram import scrape_telegram
from scraping.youtube import scrape_youtube


app = FastAPI()

# Servir carpeta static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Modelo de entrada
class UserInput(BaseModel):
    username: str

# SERVIR EL HTML EN LA RAÍZ /
@app.get("/")
def root():
    return FileResponse("static/index.html")


@app.post("/scrape/instagram")
def instagram_scraper(data: UserInput = Body(...)):
    username = data.username
    try:
        data = extraer_datos_relevantes(username)
        filename = f"exports/{username}.xlsx"
        export_to_excel([data], filename)
        guardar_historial("Instagram", username, "Éxito")
        return {"data": data, "excel_path": f"/download/{username}.xlsx"}
    except Exception as e:
        guardar_historial("Instagram", username, f"Error: {str(e)}")
        return JSONResponse(status_code=400, content={"error": f"No se pudo scrapear el perfil: {str(e)}"})


@app.post("/scrape/telegram")
def telegram_scraper(data: UserInput = Body(...)):
    username = data.username
    try:
        data = scrape_telegram(username)
        filename = f"exports/telegram_{username}.xlsx"
        export_to_excel([data], filename)
        guardar_historial("Telegram", username, "Éxito")
        return {"data": data, "excel_path": f"/download/telegram_{username}.xlsx"}
    except Exception as e:
        guardar_historial("Telegram", username, f"Error: {str(e)}")
        return JSONResponse(status_code=400, content={"error": "No se pudo scrapear el canal."})



@app.post("/scrape/youtube")
def youtube_scraper(data: UserInput = Body(...)):
    username = data.username
    try:
        data = scrape_youtube(username)
        filename = f"exports/youtube_{username}.xlsx"
        export_to_excel([data], filename)
        guardar_historial("YouTube", username, "Éxito")
        return {"data": data, "excel_path": f"/download/youtube_{username}.xlsx"}
    except Exception as e:
        guardar_historial("YouTube", username, f"Error: {str(e)}")
        return JSONResponse(status_code=400, content={"error": "No se pudo scrapear el canal."})


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
        return JSONResponse(status_code=400, content={"error": f"No se pudo realizar la búsqueda web: {str(e)}"})


@app.get("/download/{filename}")
def download_excel(filename: str):
    file_path = f"exports/{filename}"
    return FileResponse(path=file_path, filename=filename,
                        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@app.get("/historial")
def ver_historial():
    try:
        with open("exports/historial.csv", newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            historial = list(reader)
        return {"historial": historial}
    except FileNotFoundError:
        return {"historial": []}


@app.delete("/historial")
def borrar_historial():
    try:
        os.remove("exports/historial.csv")
        return {"message": "Historial eliminado correctamente"}
    except FileNotFoundError:
        return {"message": "El historial ya está vacío"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Error al eliminar el historial"})


@app.get("/descargar/historial.csv")
def descargar_historial_csv():
    filepath = "exports/historial.csv"
    if not os.path.exists(filepath):
        return JSONResponse(status_code=404, content={"error": "No hay historial disponible"})
    return FileResponse(filepath, media_type='text/csv', filename="historial.csv")


@app.get("/descargar/historial.xlsx")
def descargar_historial_xlsx():
    csv_path = "exports/historial.csv"
    xlsx_path = "exports/historial.xlsx"

    if not os.path.exists(csv_path):
        return JSONResponse(status_code=404, content={"error": "No hay historial disponible"})

    if not os.path.exists(xlsx_path) or os.path.getmtime(csv_path) > os.path.getmtime(xlsx_path):
        df = pd.read_csv(csv_path)
        df.to_excel(xlsx_path, index=False)

    return FileResponse(xlsx_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        filename="historial.xlsx")
