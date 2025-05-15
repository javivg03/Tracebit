from fastapi import APIRouter, Body
from pydantic import BaseModel

from scraping.tiktok.perfil import obtener_datos_perfil_tiktok
from tasks.tiktok import scrape_followers_info_tiktok_task
from tasks.tiktok import scrape_followees_info_tiktok_task
from services.logging_config import logger
from utils.scraping_handler import procesar_scraping

router_tiktok = APIRouter(prefix="/tiktok")

# ========== Pydantic Models ==========
class UserInput(BaseModel):
    username: str
    habilitar_busqueda_web: bool = False

class SeguidoresRequest(BaseModel):
    max_seguidores: int = 10

class SeguidosRequest(BaseModel):
    max_seguidos: int = 10

# ========== Endpoints ==========
@router_tiktok.post("/perfil")
async def tiktok_scraper(data: UserInput = Body(...)):
    return await procesar_scraping(
        data.username,
        "tiktok",
        obtener_datos_perfil_tiktok,
        habilitar_busqueda_web=data.habilitar_busqueda_web
    )


@router_tiktok.post("/seguidores")
def lanzar_scraping_info_seguidores_tiktok(data: UserInput = Body(...), req: SeguidoresRequest = Body(...)):
    tarea = scrape_followers_info_tiktok_task.delay(data.username, req.max_seguidores)
    logger.info(f"📥 Tarea Celery lanzada: scrape_followers_info_tiktok para {data.username} (máx {req.max_seguidores})")
    return {"mensaje": "Scraping completo de seguidores de TikTok en curso", "tarea_id": tarea.id}

@router_tiktok.post("/seguidos")
def lanzar_scraping_info_seguidos_tiktok(data: UserInput = Body(...), req: SeguidosRequest = Body(...)):
    tarea = scrape_followees_info_tiktok_task.delay(data.username, req.max_seguidos)
    logger.info(f"📥 Tarea Celery lanzada: scrape_followees_info_tiktok para {data.username} (máx {req.max_seguidos})")
    return {"mensaje": "Scraping completo de seguidos de TikTok en curso", "tarea_id": tarea.id}