from fastapi import APIRouter, Body
from pydantic import BaseModel

from scraping.instagram.perfil import obtener_datos_perfil_instagram_con_fallback
from tasks.instagram import scrape_followers_info_task, scrape_followees_info_task
from services.logging_config import logger
from utils.scraping_handler import procesar_scraping

router_instagram = APIRouter(prefix="/instagram")

# ========== Pydantic Models ==========
class UserInput(BaseModel):
    username: str

class SeguidoresRequest(BaseModel):
    max_seguidores: int = 10

class SeguidosRequest(BaseModel):
    max_seguidos: int = 10

# ========== Endpoints ==========
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
