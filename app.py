from fastapi import FastAPI, Body
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool
import os
import pandas as pd
import traceback

# Importación de scrapers
from scraping.instagram import extraer_datos_relevantes  # SYNC
from scraping.telegram import scrape_telegram  # SYNC
from scraping.youtube import scrape_youtube  # ASYNC
from scraping.facebook import scrape_facebook  # ASYNC
from scraping.tiktok import scrape_tiktok  # ASYNC
from scraping.x import scrape_x  # ASYNC
from scraping.web import buscar_por_keyword  # SYNC

# Otros servicios
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


# Función auxiliar para procesar el scraping y, de no encontrar email, ejecutar búsqueda cruzada
async def process_scraping(platform_name: str, scraper_func, username: str, is_async: bool):
    try:
        # Ejecutar el scraper según su naturaleza (async o sync)
        if is_async:
            datos = await scraper_func(username)
        else:
            datos = await run_in_threadpool(scraper_func, username)
        if datos is None:
            raise Exception("El scraper devolvió None")
        # Si no se encontró email, se inicia la búsqueda cruzada
        if not datos.get("email"):
            print(f"No se encontró email en {platform_name}, iniciando búsqueda cruzada...")
            resultado_cruzado = await run_in_threadpool(busqueda_cruzada.buscar_contacto, username, datos.get("nombre"))
            if resultado_cruzado and (resultado_cruzado.get("email") or resultado_cruzado.get("telefono")):
                datos["email"] = resultado_cruzado.get("email")
                datos["telefono"] = resultado_cruzado.get("telefono")
                datos["fuente_email"] = resultado_cruzado.get("url_fuente")
                original_origen = datos.get("origen", "no_email")
                cross_origen = resultado_cruzado.get("origen")
                datos["origen"] = f"{original_origen} + búsqueda cruzada ({cross_origen})"
        return datos
    except Exception as e:
        raise Exception(f"{platform_name}: {str(e)}")


# Endpoint para Instagram
@app.post("/scrape/instagram")
async def instagram_scraper(data: UserInput = Body(...)):
    try:
        datos = await process_scraping("Instagram", extraer_datos_relevantes, data.username, False)
        print("✅ DATOS RECIBIDOS:", datos)
        filename = f"exports/instagram_{data.username}.xlsx"
        export_to_excel([datos], filename)
        guardar_historial("Instagram", data.username, "Éxito")
        return {"data": datos, "excel_path": f"/download/instagram_{data.username}.xlsx"}
    except Exception as e:
        print("❌ EXCEPCIÓN EN Instagram")
        print(traceback.format_exc())
        return JSONResponse(status_code=400, content={"error": f"No se pudo scrapear Instagram: {str(e)}"})


# Endpoint para YouTube
@app.post("/scrape/youtube")
async def youtube_scraper(data: UserInput = Body(...)):
    try:
        datos = await process_scraping("YouTube", scrape_youtube, data.username, True)
        print("✅ DATOS RECIBIDOS:", datos)
        filename = f"exports/youtube_{data.username}.xlsx"
        export_to_excel([datos], filename)
        guardar_historial("YouTube", data.username, "Éxito")
        return {"data": datos, "excel_path": f"/download/youtube_{data.username}.xlsx"}
    except Exception as e:
        print("❌ EXCEPCIÓN EN YouTube")
        print(traceback.format_exc())
        return JSONResponse(status_code=400, content={"error": f"No se pudo scrapear YouTube: {str(e)}"})


# Endpoint para Facebook
@app.post("/scrape/facebook")
async def facebook_scraper(data: UserInput = Body(...)):
    try:
        datos = await process_scraping("Facebook", scrape_facebook, data.username, True)
        print("✅ DATOS RECIBIDOS:", datos)
        filename = f"exports/facebook_{data.username}.xlsx"
        export_to_excel([datos], filename)
        guardar_historial("Facebook", data.username, "Éxito")
        return {"data": datos, "excel_path": f"/download/facebook_{data.username}.xlsx"}
    except Exception as e:
        print("❌ EXCEPCIÓN EN Facebook")
        print(traceback.format_exc())
        return JSONResponse(status_code=400, content={"error": f"No se pudo scrapear Facebook: {str(e)}"})


# Endpoint para TikTok
@app.post("/scrape/tiktok")
async def tiktok_scraper(data: UserInput = Body(...)):
    try:
        datos = await process_scraping("TikTok", scrape_tiktok, data.username, True)
        print("✅ DATOS RECIBIDOS:", datos)
        filename = f"exports/tiktok_{data.username}.xlsx"
        export_to_excel([datos], filename)
        guardar_historial("TikTok", data.username, "Éxito")
        return {"data": datos, "excel_path": f"/download/tiktok_{data.username}.xlsx"}
    except Exception as e:
        print("❌ EXCEPCIÓN EN TikTok")
        print(traceback.format_exc())
        return JSONResponse(status_code=400, content={"error": f"No se pudo scrapear TikTok: {str(e)}"})


# Endpoint para X (Twitter)
@app.post("/scrape/x")
async def x_scraper(data: UserInput = Body(...)):
    try:
        datos = await process_scraping("X", scrape_x, data.username, True)
        print("✅ DATOS RECIBIDOS:", datos)
        filename = f"exports/x_{data.username}.xlsx"
        export_to_excel([datos], filename)
        guardar_historial("X", data.username, "Éxito")
        return {"data": datos, "excel_path": f"/download/x_{data.username}.xlsx"}
    except Exception as e:
        print("❌ EXCEPCIÓN EN X")
        print(traceback.format_exc())
        return JSONResponse(status_code=400, content={"error": f"No se pudo scrapear X: {str(e)}"})


# Endpoint para Web (búsqueda por keyword)
@app.post("/scrape/web")
async def web_scraper(data: UserInput = Body(...)):
    try:
        # Ejecutar la búsqueda por keyword en un threadpool
        resultados = await run_in_threadpool(buscar_por_keyword, data.username)
        if not resultados or not isinstance(resultados, list) or len(resultados) == 0:
            raise Exception("El scraper devolvió una lista vacía")

        # Para cada resultado sin email, se ejecuta búsqueda cruzada concurrentemente
        from concurrent.futures import ThreadPoolExecutor

        def actualizar_resultado(result):
            if not result.get("email"):
                print(f"Iniciando búsqueda cruzada para: {result.get('titulo')}")
                cross = busqueda_cruzada.buscar_contacto(data.username, result.get("titulo"))
                if cross and (cross.get("email") or cross.get("telefono")):
                    result["email"] = cross.get("email")
                    result["telefono"] = cross.get("telefono")
                    result["fuente_email"] = cross.get("url_fuente")
                    original_origen = result.get("origen", "no_email")
                    cross_origen = cross.get("origen")
                    result["origen"] = f"{original_origen} + búsqueda cruzada ({cross_origen})"
            return result

        with ThreadPoolExecutor() as executor:
            resultados_actualizados = list(executor.map(actualizar_resultado, resultados))

        print("✅ Resultados obtenidos:", resultados_actualizados)
        filename = f"exports/web_{data.username.replace(' ', '_')}.xlsx"
        export_to_excel(resultados_actualizados, filename)
        guardar_historial("Web", data.username, "Éxito")
        return {"data": resultados_actualizados, "excel_path": f"/download/web_{data.username.replace(' ', '_')}.xlsx"}
    except Exception as e:
        print("❌ EXCEPCIÓN EN Web")
        print(traceback.format_exc())
        return JSONResponse(status_code=400, content={"error": f"No se pudo scrapear Web: {str(e)}"})
