import os
import csv
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.encoders import jsonable_encoder
from celery.result import AsyncResult
from celery_app import celery_app
from services.logging_config import logger

from utils.history import obtener_resultado_temporal
from exports.exporter import exportar_resultados_a_excel, exportar_resultados_a_csv

router_resultados = APIRouter()

# ─────────────────────────────────────────────────────────────
# 📁 Exportar resultados bajo demanda
# ─────────────────────────────────────────────────────────────

@router_resultados.get("/exportar/perfil/{username}")
def exportar_perfil(username: str, tipo: str = Query("excel", enum=["excel", "csv"])):
    resultado = obtener_resultado_temporal("perfil", username)

    if not resultado:
        return JSONResponse(status_code=404, content={"error": "No hay datos disponibles para exportar"})

    nombre_archivo = f"perfil_{username}"

    if tipo == "csv":
        ruta = exportar_resultados_a_csv([resultado], nombre_archivo)
        mime_type = "text/csv"
    else:
        ruta = exportar_resultados_a_excel([resultado], nombre_archivo)
        mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    if not ruta or not os.path.exists(ruta):
        return JSONResponse(status_code=500, content={"error": "Error al generar el archivo de exportación"})

    return FileResponse(path=ruta, filename=os.path.basename(ruta), media_type=mime_type)


@router_resultados.get("/exportar/tarea/{tipo}/{username}")
def exportar_tarea(tipo: str, username: str, formato: str = Query("excel", enum=["excel", "csv"])):
    """
    Exporta resultados de tareas (seguidores, seguidos, tweets...) bajo demanda.
    """
    datos = obtener_resultado_temporal(tipo, username)

    if not datos:
        return JSONResponse(status_code=404, content={"error": "No hay datos para exportar"})

    nombre_archivo = f"{tipo}_{username}"

    if formato == "csv":
        ruta = exportar_resultados_a_csv(datos, nombre_archivo)
        mime = "text/csv"
    else:
        ruta = exportar_resultados_a_excel(datos, nombre_archivo)
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    if not ruta or not os.path.exists(ruta):
        return JSONResponse(status_code=500, content={"error": "Error al generar el archivo"})

    return FileResponse(path=ruta, filename=os.path.basename(ruta), media_type=mime)

# ─────────────────────────────────────────────────────────────
# 📦 Resultado de tarea Celery
# ─────────────────────────────────────────────────────────────

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

        return datos

    except Exception as e:
        logger.exception("❌ Excepción al recuperar resultado:")
        return JSONResponse(status_code=500, content={"estado": "error", "mensaje": str(e)})

# ─────────────────────────────────────────────────────────────
# 🛑 Cancelar tarea Celery
# ─────────────────────────────────────────────────────────────

@router_resultados.post("/cancelar-tarea/{tarea_id}")
def cancelar_tarea(tarea_id: str):
    resultado = AsyncResult(tarea_id, app=celery_app)
    if resultado and resultado.state in ["PENDING", "STARTED"]:
        resultado.revoke(terminate=True)
        logger.info(f"🛑 Tarea {tarea_id} cancelada manualmente.")
        return {"estado": "cancelada", "mensaje": "La tarea ha sido cancelada."}

    return {"estado": "no_cancelada", "mensaje": "No se pudo cancelar (ya finalizada o desconocida)."}

# ─────────────────────────────────────────────────────────────
# 📋 Historial de búsquedas (CSV + Excel)
# ─────────────────────────────────────────────────────────────

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


@router_resultados.delete("/historial")
def borrar_historial():
    try:
        with open("exports/historial.csv", "w", encoding='utf-8') as archivo:
            archivo.write("fecha,plataforma,tipo,usuario,resultado,archivo\n")

        xlsx_path = "exports/historial.xlsx"
        if os.path.exists(xlsx_path):
            os.remove(xlsx_path)

        return {"mensaje": "Historial borrado"}

    except Exception as e:
        logger.error(f"❌ Error al borrar historial: {e}")
        return JSONResponse(content={"detalle": "Error al borrar historial"}, status_code=500)


@router_resultados.get("/descargar/historial.csv")
def descargar_historial_csv():
    path = "exports/historial.csv"
    if os.path.exists(path):
        return FileResponse(path, filename="historial.csv", media_type="text/csv")
    return JSONResponse(status_code=404, content={"error": "Archivo CSV no encontrado"})


@router_resultados.get("/descargar/historial.xlsx")
def descargar_historial_excel():
    path = "exports/historial.xlsx"
    if os.path.exists(path):
        return FileResponse(path, filename="historial.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    return JSONResponse(status_code=404, content={"error": "Archivo Excel no encontrado"})


@router_resultados.get("/descargar/{nombre_archivo}")
async def descargar_archivo(nombre_archivo: str):
    ruta = f"exports/{nombre_archivo}"
    if os.path.exists(ruta):
        return FileResponse(path=ruta, filename=nombre_archivo, media_type='application/octet-stream')
    else:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")