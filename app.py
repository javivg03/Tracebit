from fastapi import FastAPI, APIRouter, Body
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool
from celery.result import AsyncResult
from fastapi.encoders import jsonable_encoder
from celery_app import celery_app
import traceback

from services.logging_config import logger

from scraping.instagram.perfil import obtener_datos_perfil_instagram_con_fallback
from scraping.tiktok.perfil import obtener_datos_perfil_tiktok

from tasks.instagram import scrape_followers_info_task, scrape_followees_info_task
from tasks.tiktok import scrape_followers_info_tiktok_task

from exports.exporter import export_to_excel
from utils.history import guardar_historial

# ========== FASTAPI APP SETUP ==========
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# ========== Pydantic Models ==========
class UserInput(BaseModel):
    username: str

class SeguidoresRequest(BaseModel):
    max_seguidores: int = 10

class SeguidosRequest(BaseModel):
    max_seguidos: int = 10

# ========== Reutilizable scraping handler ==========
async def procesar_scraping(username: str, red: str, funcion_scraper):
    logger.info(f"🚀 Iniciando scraping de perfil {red.upper()} para: {username}")
    datos = await run_in_threadpool(funcion_scraper, username)

    if datos and datos.get("email"):
        path = f"exports/{red}_{username}.xlsx"
        export_to_excel([datos], path)
        guardar_historial(f"{red.capitalize()} - Perfil", username, "Éxito")
        logger.info(f"✅ Scraping de perfil completado para {username}, datos exportados.")
        return {"data": datos, "excel_path": f"/download/{red}_{username}.xlsx"}

    logger.warning(f"⚠️ Scraping completado pero sin email para: {username}")
    return {"data": datos, "excel_path": None}

# ========== Instagram Endpoints ==========
router_instagram = APIRouter(prefix="/instagram")

@router_instagram.post("/perfil")
async def instagram_scraper(data: UserInput = Body(...)):
    return await procesar_scraping(data.username, "instagram", obtener_datos_perfil_instagram_con_fallback)

@router_instagram.post("/seguidores")
def lanzar_scraping_info_seguidores(data: UserInput = Body(...), req: SeguidoresRequest = Body(...)):
    tarea = scrape_followers_info_task.delay(data.username, req.max_seguidores)
    logger.info(f"📥 Tarea Celery lanzada: scrape_followers_info para {data.username} (máx {req.max_seguidores})")
    return {"mensaje": "Scraping completo de seguidores en curso", "tarea_id": tarea.id}

@router_instagram.post("/seguidos")
def lanzar_scraping_info_seguidos(data: UserInput = Body(...), req: SeguidosRequest = Body(...)):
    tarea = scrape_followees_info_task.delay(data.username, req.max_seguidos)
    logger.info(f"📥 Tarea Celery lanzada: scrape_followees_info para {data.username} (máx {req.max_seguidos})")
    return {"mensaje": "Scraping completo de seguidos en curso", "tarea_id": tarea.id}

# ========== TikTok Endpoints ==========
router_tiktok = APIRouter(prefix="/tiktok")

@router_tiktok.post("/perfil")
async def tiktok_scraper(data: UserInput = Body(...)):
    return await procesar_scraping(data.username, "tiktok", obtener_datos_perfil_tiktok)

@router_tiktok.post("/seguidores")
def lanzar_scraping_info_seguidores_tiktok(data: UserInput = Body(...), req: SeguidoresRequest = Body(...)):
    tarea = scrape_followers_info_tiktok_task.delay(data.username, req.max_seguidores)
    logger.info(f"📥 Tarea Celery lanzada: scrape_followers_info_tiktok para {data.username} (máx {req.max_seguidores})")
    return {"mensaje": "Scraping completo de seguidores de TikTok en curso", "tarea_id": tarea.id}

# ========== Task result checker ==========
@app.get("/resultado-tarea/{tarea_id}")
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

# ========== Static HTML ==========
@app.get("/")
def root():
    return FileResponse("static/index.html")

# ========== Include Routers ==========
app.include_router(router_instagram)
app.include_router(router_tiktok)
# ⚠️ Cuando crees Telegram, Facebook, etc. solo añade su router aquí
# app.include_router(router_telegram)
# app.include_router(router_facebook)
# app.include_router(router_youtube)
# app.include_router(router_x)
