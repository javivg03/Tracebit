from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from celery.result import AsyncResult
from celery_app import celery_app
from services.logging_config import logger

router_resultados = APIRouter()

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
        if not datos:
            return {"estado": "sin_datos", "mensaje": "La tarea no devolvió información válida"}

        logger.info(f"✅ Resultado obtenido correctamente de la tarea {tarea_id}")
        return JSONResponse(content=jsonable_encoder(datos))

    except Exception as e:
        logger.exception("❌ Excepción al recuperar resultado:")
        return JSONResponse(status_code=500, content={"estado": "error", "mensaje": str(e)})
