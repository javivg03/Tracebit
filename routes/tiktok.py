from fastapi import APIRouter
from pydantic import BaseModel

from scraping.tiktok.perfil import obtener_datos_perfil_tiktok
from tasks.tiktok import scrape_followers_info_tiktok_task
from tasks.tiktok import scrape_followees_info_tiktok_task
from services.logging_config import logger
from utils.scraping_handler import procesar_scraping

router_tiktok = APIRouter(prefix="/tiktok")

# ========== Pydantic Models ==========

class PerfilInput(BaseModel):
    username: str
    habilitar_busqueda_web: bool = False

class SeguidoresInput(BaseModel):
    username: str
    habilitar_busqueda_web: bool = False
    max_seguidores: int = 10

class SeguidosInput(BaseModel):
    username: str
    max_seguidos: int = 10

# ========== Endpoints ==========

@router_tiktok.post("/perfil")
async def tiktok_scraper(data: PerfilInput):
    logger.info(f"📥 Endpoint recibido: Scraping de perfil TikTok para {data.username}")
    return await procesar_scraping(
        data.username,
        "tiktok",
        obtener_datos_perfil_tiktok,
        habilitar_busqueda_web=data.habilitar_busqueda_web
    )

@router_tiktok.post("/seguidores")
def lanzar_scraping_info_seguidores_tiktok(data: SeguidoresInput):
    tarea = scrape_followers_info_tiktok_task.delay(data.username, data.max_seguidores)
    logger.info(f"📨 Petición recibida para scrapear seguidores de {data.username}")
    return {"mensaje": "Scraping completo de seguidores de TikTok en curso", "tarea_id": tarea.id}

@router_tiktok.post("/seguidos")
def lanzar_scraping_info_seguidos_tiktok(data: SeguidosInput):
    tarea = scrape_followees_info_tiktok_task.delay(data.username, data.max_seguidos)
    logger.info(f"📨 Petición recibida para scrapear seguidos de {data.username}")
    return {"mensaje": "Scraping completo de seguidos de TikTok en curso", "tarea_id": tarea.id}
