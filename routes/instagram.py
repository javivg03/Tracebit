from fastapi import APIRouter
from pydantic import BaseModel
from services.logging_config import logger
from utils.flujo_scraping import flujo_scraping_multired
from tasks.instagram import scrape_followers_info_task, scrape_followees_info_task

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
	logger.info(f"📥 Endpoint recibido: Scraping de perfil Instagram para {data.username}")
	return await flujo_scraping_multired(
		username=data.username,
		redes=["instagram", "tiktok"],
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
