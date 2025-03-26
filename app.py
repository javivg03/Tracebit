import csv
import os
import requests
import pandas as pd
from services.serper import buscar_en_google
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from scraping.instagram import scrape_profile
from exports.exporter import export_to_excel
from fastapi.responses import JSONResponse
from services.history import guardar_historial
from scraping.telegram import scrape_telegram

app = FastAPI()

# Servir carpeta static
app.mount("/static", StaticFiles(directory="static"), name="static")


# SERVIR EL HTML EN LA RAÍZ /
@app.get("/")
def root():
    return FileResponse("static/index.html")


@app.post("/scrape/instagram")
def instagram_scraper(username: str):
    try:
        data = scrape_profile(username)
        filename = f"exports/{username}.xlsx"
        export_to_excel([data], filename)
        guardar_historial("Instagram", username, "Éxito")

        # 🔁 ENVIAR A N8N DESPUÉS DE SCRAPEAR
        try:
            response = requests.post(
                "http://localhost:5678/webhook/scraping-instagram",
                json=data,
                timeout=5
            )
            if response.status_code != 200:
                print("⚠️ Fallo al enviar datos a n8n:", response.text)
        except Exception as e:
            print("❌ Error al contactar con n8n:", str(e))

        return {
            "data": data,
            "excel_path": f"/download/{username}.xlsx"
        }
    except Exception as e:
        guardar_historial("Instagram", username, f"Error: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"error": f"No se pudo scrapear el perfil: {str(e)}"}
        )



@app.post("/scrape/telegram")
def telegram_scraper(username: str):
    try:
        data = scrape_telegram(username)
        filename = f"exports/telegram_{username}.xlsx"
        export_to_excel([data], filename)
        guardar_historial("Telegram", username, "Éxito")
        return {
            "data": data,
            "excel_path": f"/download/telegram_{username}.xlsx"
        }
    except Exception as e:
        guardar_historial("Telegram", username, f"Error: {str(e)}")
        return JSONResponse(status_code=400, content={"error": "No se pudo scrapear el canal."})


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

    # Convertir CSV a XLSX solo si no existe o si está desactualizado
    if not os.path.exists(xlsx_path) or os.path.getmtime(csv_path) > os.path.getmtime(xlsx_path):
        df = pd.read_csv(csv_path)
        df.to_excel(xlsx_path, index=False)

    return FileResponse(xlsx_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        filename="historial.xlsx")


@app.get("/buscar_google")
def buscar_google(query: str):
    try:
        resultados = buscar_en_google(query)
        return {
            "resultados": resultados.get("organic", [])[:5]
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
