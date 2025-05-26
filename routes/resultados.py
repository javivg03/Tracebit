import os
import csv
from fastapi import APIRouter
from fastapi.responses import JSONResponse, FileResponse
from fastapi.encoders import jsonable_encoder
from celery.result import AsyncResult
from celery_app import celery_app
from services.logging_config import logger

router_resultados = APIRouter()


# 📦 Recuperar el estado y resultado de una tarea Celery
@router_resultados.get("/resultado-tarea/{tarea_id}")
def obtener_resultado_tarea(tarea_id: str):
    resultado = AsyncResult(tarea_id, app=celery_app)

    if not resultado.ready():
        return {"estado": "pendiente"}

    if resultado.failed():
        logger.error(f"❌ La tarea {tarea_id} falló.")
        logger.error(f"Traceback:\n{resultado.traceback}")
        return {"estado": "error", "mensaje": "La tarea falló"}

    try:
        datos = resultado.get()

        if not datos or not isinstance(datos, dict) or "estado" not in datos:
            return {"estado": "sin_datos", "mensaje": "La tarea no devolvió información válida"}

        logger.info(f"✅ Resultado obtenido correctamente de la tarea {tarea_id}")
        return JSONResponse(content=jsonable_encoder(datos))

    except Exception as e:
        logger.exception("❌ Excepción al recuperar resultado:")
        return JSONResponse(status_code=500, content={"estado": "error", "mensaje": str(e)})


# 🛑 Cancelar una tarea en ejecución (si aún está activa)
@router_resultados.post("/cancelar-tarea/{tarea_id}")
def cancelar_tarea(tarea_id: str):
    resultado = AsyncResult(tarea_id, app=celery_app)
    if resultado and resultado.state in ["PENDING", "STARTED"]:
        resultado.revoke(terminate=True)
        logger.info(f"🛑 Tarea {tarea_id} cancelada manualmente.")
        return {"estado": "cancelada", "mensaje": "La tarea ha sido cancelada."}

    return {"estado": "no_cancelada", "mensaje": "No se pudo cancelar (ya finalizada o desconocida)."}


# 📋 Consultar el historial completo (como JSON para frontend)
@router_resultados.get("/historial")
def obtener_historial():
    try:
        historial_path = "exports/historial.csv"

        if not os.path.exists(historial_path):
            return JSONResponse(content=[], status_code=200)

        with open(historial_path, newline='', encoding='utf-8') as archivo:
            lector = csv.DictReader(archivo)
            historial = [fila for fila in lector]
            return JSONResponse(content=historial, status_code=200)

    except Exception as e:
        logger.error(f"❌ Error al obtener historial: {e}")
        return JSONResponse(content={"error": "Error al obtener historial"}, status_code=500)


# 🧹 Borrar el historial y dejar solo el encabezado
@router_resultados.delete("/historial")
def borrar_historial():
    try:
        with open("exports/historial.csv", "w", encoding='utf-8') as archivo:
            archivo.write("fecha,plataforma,usuario,resultado\n")
        # También borramos historial.xlsx si existe
        xlsx_path = "exports/historial.xlsx"
        if os.path.exists(xlsx_path):
            os.remove(xlsx_path)
        return {"mensaje": "Historial borrado"}
    except Exception as e:
        logger.error(f"❌ Error al borrar historial: {e}")
        return JSONResponse(content={"detalle": "Error al borrar historial"}, status_code=500)


# 📥 Descargar el historial en CSV
@router_resultados.get("/descargar/historial.csv")
def descargar_historial_csv():
    path = "exports/historial.csv"
    if os.path.exists(path):
        return FileResponse(path, filename="historial.csv", media_type="text/csv")
    return JSONResponse(status_code=404, content={"error": "Archivo CSV no encontrado"})


# 📥 Descargar el historial en XLSX
@router_resultados.get("/descargar/historial.xlsx")
def descargar_historial_excel():
    path = "exports/historial.xlsx"
    if os.path.exists(path):
        return FileResponse(path, filename="historial.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    return JSONResponse(status_code=404, content={"error": "Archivo Excel no encontrado"})
