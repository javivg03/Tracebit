from fastapi import APIRouter
from pydantic import BaseModel

from scraping.instagram.perfil import obtener_datos_perfil_instagram_con_fallback
from tasks.instagram import scrape_followers_info_task, scrape_followees_info_task
from services.logging_config import logger
from utils.scraping_handler import procesar_scraping

router_instagram = APIRouter(prefix="/instagram")


# ========== Pydantic Models ==========

class InstagramPerfilInput(BaseModel):
	username: str
	habilitar_busqueda_web: bool = False


class SeguidoresInput(BaseModel):
	username: str
	max_seguidores: int = 10


class SeguidosInput(BaseModel):
	username: str
	max_seguidos: int = 10


# ========== Endpoints ==========

@router_instagram.post("/perfil")
async def instagram_scraper(data: InstagramPerfilInput):
	return await procesar_scraping(
		data.username,
		"instagram",
		obtener_datos_perfil_instagram_con_fallback,
		habilitar_busqueda_web=data.habilitar_busqueda_web
	)


@router_instagram.post("/seguidores")
def lanzar_scraping_info_seguidores(data: SeguidoresInput):
	tarea = scrape_followers_info_task.delay(data.username, data.max_seguidores)
	logger.info(f"📨 Petición recibida para scrapear seguidores de {data.username}")
	return {"mensaje": "Scraping completo de seguidores en curso", "tarea_id": tarea.id}


@router_instagram.post("/seguidos")
def lanzar_scraping_info_seguidos(data: SeguidosInput):
	tarea = scrape_followees_info_task.delay(data.username, data.max_seguidos)
	logger.info(f"📨 Petición recibida para scrapear seguidos de {data.username}")
	return {"mensaje": "Scraping completo de seguidos en curso", "tarea_id": tarea.id}
